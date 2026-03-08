package main // This tells Go that this file is the "entry point" or the start of our program.

import (
	"net/http" // Standard library to handle HTTP status codes (like 200 OK or 400 Bad Request).
	"os"       // Allows us to talk to the Operating System, specifically to check for environment variables.
	"sync"     // Provides "WaitGroups" which help us wait for multiple background tasks to finish.

	"parallax-ai/go-scraper/internal/scraper" // This imports our own custom scraping logic from the internal folder.

	"github.com/gin-gonic/gin" // A popular web framework that makes it easy to build APIs and handle routes.
)

// ScrapeRequest is a "template" or "blueprint" for the data we expect to receive.
type ScrapeRequest struct {
	// We expect a JSON object with a field called "urls" which is a list (slice) of strings.
	URLs []string `json:"urls"`
}

func main() {
	r := gin.Default() // Create a default instance of the Gin web server with logging and recovery built-in.

	// Define a "POST" route at "/scrape". This is the endpoint our Python agent will call.
	r.POST("/scrape", func(c *gin.Context) {
		var req ScrapeRequest // Create an empty variable based on our blueprint above.

		// Check if the incoming data is valid JSON. If not, tell the user what went wrong.
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()}) // Return a 400 error.
			return                                                     // Stop here if there's an error.
		}

		// Create a "Channel". Think of this as a pipe where we can throw results as they finish.
		// We make it the same size as the number of URLs so it doesn't get clogged.
		resultsCh := make(chan scraper.ScrapeResult, len(req.URLs))

		var wg sync.WaitGroup // A WaitGroup is like a counter. It helps us track how many background tasks are running.

		// Loop through every URL the user sent us.
		for _, u := range req.URLs {
			wg.Add(1) // Increment our counter for every URL we start processing.

			// Launch a "Goroutine" (a lightweight background thread).
			// This allows us to scrape all URLs at the exact same time instead of one by one.
			go func(url string) {
				defer wg.Done() // When this specific background task finishes, tell the WaitGroup we are done.

				result := scraper.ScrapeURL(url) // Call our actual scraping logic to get the page content.
				resultsCh <- result              // Throw the result into our "pipe" (channel).
			}(u) // Pass the current URL into the function.
		}

		// This line pauses the program and waits until the WaitGroup counter reaches zero.
		wg.Wait()

		// Once everything is finished, close the "pipe" so no more data can be sent.
		close(resultsCh)

		var results []scraper.ScrapeResult // Create a list to hold all the finished results.

		// "Drain" the pipe. Pull every result out of the channel and add it to our list.
		for res := range resultsCh {
			results = append(results, res)
		}

		// Finally, send the whole list back to the user as a JSON response with a 200 OK status.
		c.JSON(http.StatusOK, results)
	})

	port := os.Getenv("PORT") // Check if the environment (like Render or Heroku) provided a specific port.
	if port == "" {
		port = "8080" // If no port was provided, default to using 8080.
	}

	r.Run(":" + port) // Start the server and keep it running, listening for requests.
}

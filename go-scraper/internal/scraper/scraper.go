package scraper // We declare this file as part of the 'scraper' package so other files can import it.

import (
	"context"  // Helps us manage long-running tasks, like setting a time limit (timeout) for a request.
	"fmt"      // Standard library for formatting text strings (like printing errors).
	"net/http" // Provides the tools to make web requests (like a browser does).
	"net/url"  // Helps us parse and understand URLs (e.g., splitting "http://google.com" into parts).
	"time"     // Used to define how long durations (like 15 seconds) are.

	"github.com/go-shiori/go-readability" // A special library that smart-reads a webpage and extracts just the main article text, ignoring ads/sidebars.
)

// ScrapeResult defines the structure of the data we will return after scraping a page.
type ScrapeResult struct {
	URL     string `json:"url"`     // The original link we visited.
	Title   string `json:"title"`   // The title of the article found on the page.
	Content string `json:"content"` // The main text of the article (stripped of HTML tags and clutter).
	Status  string `json:"status"`  // "success" if it worked, or an error message if it failed.
}

// ScrapeURL is the main function. It takes a raw string (like "http://example.com") and returns a ScrapeResult.
func ScrapeURL(rawURL string) ScrapeResult {
	// First, we check if the string provided is actually a valid URL structure.
	parsedURL, err := url.Parse(rawURL)
	if err != nil {
		// If the URL is broken (e.g. "ht:tp//bad"), return an error result immediately.
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Invalid URL: %v", err),
		}
	}

	// Create a "Context" with a strict 15-second timer.
	// This ensures that if a website is frozen or taking too long, we don't wait forever.
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	// "defer" means "run this function at the very end of ScrapeURL".
	// It cleans up the timer resources so we don't leak memory.
	defer cancel()

	// Create a new HTTP GET request. Note we pass 'ctx' so the request knows about our 15-second timer.
	req, err := http.NewRequestWithContext(ctx, "GET", rawURL, nil)
	if err != nil {
		// If we couldn't even build the request object, return the error.
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error creating request: %v", err),
		}
	}
	// Important: We set the "User-Agent" header to pretend we are a real Chrome browser on Windows.
	// Many websites block "bots" or empty user agents, so this helps us get past simple blocks.
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

	// Create an HTTP client to actually send the request.
	client := &http.Client{}
	// "client.Do(req)" sends the request across the internet and waits for the response.
	resp, err := client.Do(req)
	if err != nil {
		// If the network failed (e.g. DNS error, no internet, timeout), return the error.
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error executing request: %v", err),
		}
	}
	// Ensure the connection to the website is closed when we are done reading, to free up network sockets.
	defer resp.Body.Close()

	// Check the HTTP Status Code. Codes 400 and above mean something went wrong (like 404 Not Found or 500 Server Error).
	if resp.StatusCode >= 400 {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("HTTP Error: %s", resp.Status),
		}
	}

	// This is the magic part. 'readability.FromReader' takes the raw HTML stream (resp.Body) and analyzes it.
	// It figures out what part of the page is the actual story/article and throws away headers, footers, and ads.
	article, err := readability.FromReader(resp.Body, parsedURL)
	if err != nil {
		// If the library couldn't figure out the content, return an error.
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error parsing content: %v", err),
		}
	}

	// If we got here, everything worked! Return the nice clean title and content.
	return ScrapeResult{
		URL:     rawURL,
		Title:   article.Title,
		Content: article.TextContent, // TextContent is just the text, no HTML tags.
		Status:  "success",
	}
}

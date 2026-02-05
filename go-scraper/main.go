package main

import (
	"net/http"
	"os"
	"sync"

	"parallax-ai/go-scraper/internal/scraper"

	"github.com/gin-gonic/gin"
)

type ScrapeRequest struct {
	URLs []string `json:"urls"`
}

func main() {
	r := gin.Default()

	r.POST("/scrape", func(c *gin.Context) {
		var req ScrapeRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		resultsCh := make(chan scraper.ScrapeResult, len(req.URLs))
		var wg sync.WaitGroup

		for _, u := range req.URLs {
			wg.Add(1)
			go func(url string) {
				defer wg.Done()
				result := scraper.ScrapeURL(url)
				resultsCh <- result
			}(u)
		}

		// wait for everything to finish
		wg.Wait()
		close(resultsCh)

		var results []scraper.ScrapeResult
		for res := range resultsCh {
			results = append(results, res)
		}

		c.JSON(http.StatusOK, results)
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	r.Run(":" + port)
}

package scraper

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"time"

	"github.com/go-shiori/go-readability"
)

type ScrapeResult struct {
	URL     string `json:"url"`
	Title   string `json:"title"`
	Content string `json:"content"`
	Status  string `json:"status"`
}

func ScrapeURL(rawURL string) ScrapeResult {
	parsedURL, err := url.Parse(rawURL)
	if err != nil {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Invalid URL: %v", err),
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", rawURL, nil)
	if err != nil {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error creating request: %v", err),
		}
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error executing request: %v", err),
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("HTTP Error: %s", resp.Status),
		}
	}

	article, err := readability.FromReader(resp.Body, parsedURL)
	if err != nil {
		return ScrapeResult{
			URL:    rawURL,
			Status: fmt.Sprintf("Error parsing content: %v", err),
		}
	}

	return ScrapeResult{
		URL:     rawURL,
		Title:   article.Title,
		Content: article.TextContent,
		Status:  "success",
	}
}

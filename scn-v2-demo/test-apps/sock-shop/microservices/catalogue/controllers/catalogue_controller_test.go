package controllers

import (
	"bytes"
	"catalogue/models"
	"encoding/json"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestFetchCatalogues(t *testing.T) {
	e := echo.New()

	b := models.ListRequest{
		Tags:     []string{"red", "sport"},
		Order:    "",
		PageNum:  1,
		PageSize: 5,
	}

	requestByte, _ := json.Marshal(b)
	requestReader := bytes.NewReader(requestByte)

	req := httptest.NewRequest(echo.GET, "/catalogue", requestReader)
	req.Header.Set("Content-Type", "application/json")

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetPath("/catalogue")

	if assert.NoError(t, FetchSocks(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}

}
func TestCountCatalogue(t *testing.T) {
	e := echo.New()

	b := models.CountRequest{Tags:[]string{"blue", "action"}}

	requestByte, _ := json.Marshal(b)
	requestReader := bytes.NewReader(requestByte)

	req := httptest.NewRequest(echo.GET, "/catalogue/size", requestReader)
	req.Header.Set("Content-Type", "application/json")

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetPath("/catalogue/size")

	if assert.NoError(t, CountSocks(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}

func TestFetchSocksById(t *testing.T) {
	e := echo.New()
	b := models.GetRequest{ID: "6d62d909-f957-430e-8689-b5129c0bb75e"}

	requestByte, _ := json.Marshal(b)
	requestReader := bytes.NewReader(requestByte)
	req := httptest.NewRequest(echo.GET, "/catalogue/{id}", requestReader)
	req.Header.Set("Content-Type", "application/json")

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetPath("/catalogue/{id}")

	if assert.NoError(t, FetchSockById(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}

func TestGetTags(t *testing.T) {
	e := echo.New()

	req := httptest.NewRequest(echo.GET, "/tags", nil)
	req.Header.Set("Content-Type", "application/json")

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetPath("/tags")

	if assert.NoError(t, FetchTags(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}

func TestGetHealth(t *testing.T) {
	e := echo.New()
	b := models.HealthRequest{}

	requestByte, _ := json.Marshal(b)
	requestReader := bytes.NewReader(requestByte)

	req := httptest.NewRequest(echo.GET, "/health", requestReader)
	req.Header.Set("Content-Type", "application/json")

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetPath("/health")

	if assert.NoError(t, Health(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}

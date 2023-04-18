package middleware

import (
	"log"
	"net/http"
	"strings"

	"github.com/labstack/echo"
)

func CheckCookie(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        cookie, err := c.Cookie("sessionID")
        if err != nil {
            if strings.Contains(err.Error(), "named cookie not present") {
                return c.String(http.StatusUnauthorized, "you dont have any cookie")
            }

            log.Println(err)
            return err
        }

        if cookie.Value == "some_string" {
            return next(c)
        }

        return c.String(http.StatusUnauthorized, "you dont have the right cookie, cookie")
    }
}

/* func Authenticate (username, password string, s services.Service, c echo.Context) (bool, error) {
	fmt.Println("Authentication", username, password)
    u, err := s.Login(username, password)
	if username == "m5" && password == "m5" {
		
		cookie := &http.Cookie{
			Name:       "sessionID",
			Value:      "some_string",
			Expires:    time.Now().Add(48 * time.Hour),

		}
        c.SetCookie(cookie)

		return true, nil
	}
	return false, nil
} */
package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
)

func main() {
	// Get environment variables
	var broker, brokerMissing = os.LookupEnv("LMI_BROKER")
	var port, portMissing = os.LookupEnv("LMI_BROKER_PORT")
	var portNumber = 1883 // Set a reasonable default.
	var lmiTemplates, lmiTemplatesMissing = os.LookupEnv("LMI_TEMPLATES")
	var lmiStatic, lmiStaticMissing = os.LookupEnv("LMI_STATIC")

	var timeout, timeoutMissing = os.LookupEnv("LMI_TIMEOUT")
	var timeoutPeriod = 45 // Set a reasonable default.

	// Make sure the variables actually exist
	if !brokerMissing {
		fmt.Println("Error! MQTT Broker not specified.")
		return
	}

	if !portMissing {
		fmt.Println("Warning! MQTT Port not specified. Defaulting to 1883...")
	} else {
		portNumber, _ = strconv.Atoi(port)
	}

	if !lmiTemplatesMissing {
		fmt.Println("Error! LMI_TEMPLATES not specified.")
		return
	}

	if !lmiStaticMissing {
		fmt.Println("Error! LMI_STATIC not specified.")
		return
	}

	if !timeoutMissing {
		fmt.Println("Warning! Timeout not specified. Defaulting to ", timeoutPeriod, "...")
	} else {
		timeoutPeriod, _ = strconv.Atoi(timeout)
	}

	fmt.Println(" MQTT broker = ", broker, ", port = ", portNumber)

	// Gin Setup
	r := gin.Default()
	r.SetTrustedProxies([]string{"0.0.0.0"})

	r.LoadHTMLGlob(lmiTemplates)
	r.Static("/static", lmiStatic)

	// ===== Route definitions =====

	// Homepage
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "home.tmpl", gin.H{
			"location_map": location_map,
		})
	})

	r.GET("/knock/socket/:location", knockHandler)

	r.Run()
}

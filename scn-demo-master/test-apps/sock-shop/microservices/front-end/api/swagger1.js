const swaggerAutogen = require('swagger-autogen')()

const outputFile = '.swagger_output.js'
const endpointsFiles = ['./endpoints.js']

swaggerAutogen(outputFile, endpointFiles).then(() => {
	require('orders/index.js')
})

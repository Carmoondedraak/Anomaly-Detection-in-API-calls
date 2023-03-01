#!/bin/bash


source ./paypal.env

if [ ! -f "./paypal.env" ]; then
    echo "./paypal.env does not exist. You need to create one. File should contain:"
    cat <<EOF
    PAYPAL_ACCESS_CODE=[PUT CODE HERE]    
EOF
    exit
fi

result=`curl https://api-m.sandbox.paypal.com/v1/oauth2/token -s -H "Accept: application/json" -H "Accept-Language: en_US" -u ${PAYPAL_ACCESS_CODE} -d "grant_type=client_credentials" `

python3 -c "$( cat <<EOF
result=${result}
print(result['access_token'])
EOF
)"

#!/bin/bash

# SCN-SETUP
cd 001_demo_scn_setup && ./execute.sh
sleep 60
./verify.sh

# SPEC-AUDITING
cd ../002_demo_spec_auditing && ./execute.sh
sleep 10
./verify.sh

# TOKEN-INJECTION
cd ../003_demo_token_injection && ./execute.sh
sleep 10
./verify.sh


# TLS-INTERCEPTION
cd ../004_demo_tls_intercept && ./execute.sh
sleep 10
./verify.sh


# TRACE-ANALYZER
cd ../005_demo_trace_analyzer && ./execute.sh
sleep 10
./verify.sh


# FUZZING
cd ../006_demo_fuzzing && ./execute.sh
sleep 10
./verify.sh


# SPEC-RECONSTRUCTOR
cd ../007_demo_spec_reconstructor && ./execute.sh
sleep 10
./verify.sh


# CRUD-POLICIES
cd ../008_demo_crud_polcies && ./execute.sh
sleep 10
./verify.sh



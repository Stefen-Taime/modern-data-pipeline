#!/bin/bash

# Install dependencies to the 'package' directory
pip install -r requirements.txt -t ./package

# Copy the app.py file to the 'package' directory
cp app.py ./package/

# Navigate to the 'package' directory
cd package

# Create a zip archive of the 'package' directory
zip -r ../my_lambda_package.zip .

# Navigate back to the original directory
cd ..


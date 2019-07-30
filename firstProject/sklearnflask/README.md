# Flask API for scikit learn
A simple Flask application 

Refer to [this blog post](https://medium.com/@amirziai/a-flask-api-for-serving-scikit-learn-models-c8bcdaa41daa).

### Dependencies
- scikit-learn
- Flask
- pandas
- numpy

```
pip install -r requirements.txt
```

### Running API
```
python main.py <port>
```

# Endpoints
### /predict (POST)
Returns an array of predictions given a JSON object representing independent variables. Here's a sample input:
```
[
    {"Pregnancies":"6", "Glucose":"148", "BloodPressure":"72", "SkinThickness":"35", "Insulin":"0", "BMI":"33.0", "DiabetesPedigreeFunction":"0.627", "Age":"50"},
    {"Pregnancies":"1", "Glucose":"10", "BloodPressure":"36", "SkinThickness":"29", "Insulin":"0", "BMI":"10.6", "DiabetesPedigreeFunction":"0.051", "Age":"21"}
]
```

and sample output:
```
{"prediction": [0, 1]}
```


### /train (GET)
Trains the model. This is currently hard-coded to be a random forest model that is run on a subset of columns of the titanic dataset.

### /wipe (GET)
Removes the trained model.

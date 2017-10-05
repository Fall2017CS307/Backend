# Backend


# API Spec Sheet V1.0

This file documents the use of the api v1.0

 ** **
 ** **
 
## Spec sheet for url : /api/register

 This endpoint is called to register a user

### Properties spec sheet

| Parameter name | Required/Optional | use case | Accepted Value |
| :---: | :---: | :---: | :---: |
| firstname | **Required** | The firstname of the new user | String | 
| lastname | **Required** | The lastname of the new user | String |
| email | **Required** | The email of the new user | String  | 
| password | **Required** | The password for the new user | String  | 
| phone | **Required** | The phone number for the new user | String  | 


 
## Spec sheet for url : /api/login

 This endpoint is called to login a user

### Properties spec sheet

| Parameter name | Required/Optional | use case | Accepted Value |
| :---: | :---: | :---: | :---: |
| email | **Required** | The email of the new user | String  | 
| password | **Required** | The password for the new user | String  | 

### Response spec sheet

| Parameter name | Always/Sometimes | use case | Accepted Value |
| :---: | :---: | :---: | :---: |
| api | **Always** | "Datonate" | String | 
| version | **Always** | The version of the api| String |
| status | **Always** | The status code for the api call | Integer  |
 | Response | **Always** | The response string returned from the api | String |
 
 **Note**: Only the status 200, denotes a successful api call

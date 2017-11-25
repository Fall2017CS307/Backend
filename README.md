# Backend


# API Spec Sheet V1.0

This file documents the use of the api v1.0

 ** **
 ** **

#Common Routes

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


#App Specific Routes

## Spec sheet for url : /api/getExperiments/<int:user_id>

 This endpoint gets the available experiments to the user. 

### Properties spec sheet

| Parameter name | Required/Optional | use case | Accepted Value |
| :---: | :---: | :---: | :---: |

| user_id | **Required** | The user id of the user | int  |

### Response spec sheet

| Parameter name | Parent | Always/Sometimes | use case | Accepted Value |
| :---: | :---: | :---: | :---: | :---: |
| api |  NULL | **Always** | "Datonate" | String |
| version | NULL | **Always** | The version of the api| String |
| status | NULL | **Always** | The status code for the api call | Integer  |
| Response | NULL | **Always** | The response string returned from the api | String |
| experiments | NULL | **Sometimes**| Dictionary of experiment details | Dictionary | 
| id | experiments | **ALWAYS** | Id of the experiment | Int |
| price | experiments | **ALWAYS** | Price of the experiment | Int | 
| description | experiments | **ALWAYS** | Description of the experiment | String |
| isMedia | experiments | **ALWAYS** | True - Image, False - Text | True/False  |

#Web Specific Routes
 
 
 
 
 
 
 **Note**: Only the status 200, denotes a successful api call

/api/getExperiments/<int:user_id>
/api/batch/closeBatch/<int:batch_id>
/api/<int:user_id>/assign/<int:experiment_id>
/api/<int:user_id>/batchList
/api/<int:batch_id>/getBatch
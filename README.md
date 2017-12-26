# RESTful API w OAuth2.0

A RESTful API implementation of a fictional dog sitting service where the user logs in with their Google+ account (Authorized and authenticated by Google).

You can check out the Oauth2.0 section [here](https://final-project-186875.appspot.com). The API is purely back-end, but feel free to use the provided Postman JSON files to play around with the database.

Postman generated documentation is available [here](https://documenter.getpostman.com/view/2808890/cs496-final/7EBga6R#d40e6d22-2cbc-d029-da68-3475803a4db3)

*Please note, I am not affiliated with Snoop Dogg and I am not making any money off of this. I just thought it would be fun to use his name for a fictional dog sitting service. If you are affiliated with Snoop and would like me to remove his name please feel free to contact me.*

## Endpoints and Verbage:

## /
- ### ```GET```
   - View main welcome page, get an authentication token from Google

## /clients

- ### ```GET```
   - View current user’s clients
      - Header:
         - ```id_token```: user’s google_authenticated id token

      - Returns:
         - status code 200
         - all client instances in JSON format including:
            - ```id```: client id
            - ```name```: client’s name
            - ```age```: client’s age
            - ```city```: client’s city
            - ```recurring_client```: True or False
            - ```dogs```: list of user’s dogs
            - ```self```: URL path to the client


- ### ```POST```
   - Create a new client for the current user
      - Header:
         - ```id_token```: user’s google_authenticated id token
      - Body:
         - Required:
            - ```name```: client name, string
         - Optional:
            - ```age```: client’s age, integer
            - ```city```: client’s city, string
            - ```recurring_client```: True or False, bool

      - Returns:
         - Success:
            - status code 200
            - new client instance JSON including:
               - ```id```: client id
               - ```name```: client’s name
               - ```age```: client’s age or null
               - ```city```: client’s city or null
               - ```recurring_client```: True or False (default: False)
               - ```dogs```: list of user’s dogs (empty)
               - ```self```: URL path to the client
         - Failure:
            - status code 403: unauthorized
            - status code 400: bad request



## /clients/{{client id}}

- ### ``` GET```
   - View a specific client for current user
      - Header:
         - ```id_token```: user’s google_authenticated id token

      - Returns:
         - Success:
            - status code 200
            - client instance JSON including:
               - ```id```: client id
               - ```name```: client’s name
               - ```age```: client’s age
               - ```city```: client’s city
               - ```recurring_client```: True or False
               - ```dogs```: list of user’s dogs
               - ```self```: URL path to the client
         - Failure:
           - status code 403: unauthorized
            - status code 404: unable to locate resource
            - status code 400: bad request
            

- ### ```PATCH```
   - Modify an existing client
      - Header:
         -  ```id_token```: user’s google_authenticated id token
      - Optional Body Parameters:
          - ```name```: client name, string
          - ```age```: client’s age, integer
          - ```city```: client’s city, string
          - ```recurring_client```: True or False, bool
 
       - Returns:
           - Success:
               - status code 204
               - modified client instance JSON including:
                   - ```id```: client id
                   - ```name```: client’s name
                   - ```age```: client’s age
                   - ```city```: client’s city
                   - ```recurring_client```: True or False
                   - ```dogs```: list of user’s dogs
                   - ```self```: URL path to the client
           - Failure:
               - status code 403: unauthorized
               - status code 404: unable to locate resource
               - status code 400: bad request


- ### ```PUT```
    - Change a user’s client’s to/from a recurring client
        - Header:
            -  ```id_token```: user’s google_authenticated id token
        - Body:
            - ```recurring_client```: True or False, bool

        - Returns:
            - Success:
                - status code 204
                - client instance JSON including:
                    - ```id```: client id
                    - ```name```: client’s name
                    - ```age```: client’s age
                    - ```city```: client’s city
                    - ```recurring_client```: True or False
                    - ```dogs```: list of user’s dogs
                    - ```self```: URL path to the client
            - Failure:
                - status code 403: unauthorized
                - status code 404: unable to locate resource
                - status code 400: bad request


- ### ```DELETE```
    - Permanently remove a specific client in the user’s database
        - Header:
            -  ```id_token```: user’s google_authenticated id token

    - Returns:
        - Success:
            - status code 204
        - Failure:
            - status code 403: unauthorized
            - status code 404: unable to locate resource
            - status code 400: bad request
            
            

## /dogs

- ### ```GET```
    - View all current user’s client’s dogs
        - Header:
            - ```id_token```: user’s google_authenticated id token

        - Returns:
            - status code 200
            - all dog instances in JSON format including:
                - ```id```: dog id
                - ```name```: dog's name
                - ```owner```: dog owner’s id
                - ```age```: dog’s age
                - ```breed```: dog’s breed
                - ```gender```: dog’s gender: male (```m```) / female (```f```)  _  neutered (```n```) / spayed (```s```) / intact (```i```)
                    - ie ```m_i``` is an intact male and ```m_n``` is a neutered male
                - ```appointment```: approximate appointment time(s)
                - ```self```: URL path to the dog


- ### ```POST```
    - Create a new dog for the current user’s client
        - Header:
            - ```id_token```: user’s google_authenticated id token
        - Body:
            - Required:
                - ```name```: dog’s name, string
                - ```owner```: owner's id, string
            - Optional:
                - ```age```: dog's age, integer
                - ```breed```: dog's breed, string
                - ```gender```: dog’s gender, string
                - ```appointment```: approximate appointment time(s), string

        - Returns:
            - Success:
                - status code 200
                - new dog instance JSON including:
                    - ```id```: dog id
                    - ```name```: dog's name
                    - ```owner```: dog owner’s id
                    - ```age```: dog’s age
                    - ```breed```: dog’s breed
                    - ```gender```: dog’s gender: male (```m```) / female (```f```)  _  neutered (```n```) / spayed (```s```) / intact (```i```)
                        - ie ```m_i``` is an intact male and ```m_n``` is a neutered male
                    - ```appointment```: approximate appointment time(s)
                    - ```self```: URL path to the dog
            - Failure:
                - status code 403: unauthorized
                - status code 400: bad request



## /dogs/{{dog id}}

- ### ``` GET```
    - View specific client’s dog for current user
        - Header:
            - ```id_token```: user’s google_authenticated id token

        - Returns:
            - Success:
                - status code 200
                - dog instance JSON including:
                    - ```id```: dog id
                    - ```name```: dog's name
                    - ```owner```: dog owner’s id
                    - ```age```: dog’s age
                    - ```breed```: dog’s breed
                    - ```gender```: dog’s gender: male (```m```) / female (```f```)  _  neutered (```n```) / spayed (```s```) / intact (```i```)
                        - ie ```m_i``` is an intact male and ```m_n``` is a neutered male
                    - ```appointment```: approximate appointment time(s)
                    - ```self```: URL path to the dog
            - Failure:
                - status code 403: unauthorized
                - status code 404: unable to locate resource
                - status code 400: bad request


- ### ```PATCH```
    - Modify an existing client
        - Header:
            -  ```id_token```: user’s google_authenticated id token
        - Optional Body Parameters:
            - ```name```: dog’s name, string
            - ```age```: dog's age, integer
            - ```breed```: dog's breed, string
            - ```gender```: dog’s gender, string
            - ```appointment```: approximate appointment time(s), string

        - Returns:
            - Success:
                - status code 204
                - modified dog instance JSON including:
                    - ```id```: dog id
                    - ```name```: dog's name
                    - ```owner```: dog owner’s id
                    - ```age```: dog’s age
                    - ```breed```: dog’s breed
                    - ```gender```: dog’s gender: male (```m```) / female (```f```)  _  neutered (```n```) / spayed (```s```) / intact (```i```)
                        - ie ```m_i``` is an intact male and ```m_n``` is a neutered male
                    - ```appointment```: approximate appointment time(s)
                    - ```self```: URL path to the dog
            - Failure:
                - status code 403: unauthorized
                - status code 404: unable to locate resource
                - status code 400: bad request


- ### ```PUT```
    - Make an appointment for the user’s client’s dog
        - Header:
            -  ```id_token```: user’s google_authenticated id token
        - Body:
            - ```appointment```: approximate appointment time(s), string

        - Returns:
            - Success:
                - status code 204
                - dog instance JSON including:
                    - ```id```: dog id
                    - ```name```: dog's name
                    - ```owner```: dog owner’s id
                    - ```age```: dog’s age
                    - ```breed```: dog’s breed
                    - ```gender```: dog’s gender: male (```m```) / female (```f```)  _  neutered (```n```) / spayed (```s```) / intact (```i```)
                        - ie ```m_i``` is an intact male and ```m_n``` is a neutered male
                    - ```appointment```: approximate appointment time(s)
                    - ```self```: URL path to the dog
            - Failure:
                - status code 403: unauthorized
                - status code 404: unable to locate resource
                - status code 400: bad request


- ### ```DELETE```
    - Permanently remove a specific client’s dog from the user’s database
        - Header:
            -  ```id_token```: user’s google_authenticated id token

        - Returns:
            - Success:
                - status code 204
            - Failure:
                - status code 403: unauthorized
                - status code 404: unable to locate resource
                - status code 400: bad request



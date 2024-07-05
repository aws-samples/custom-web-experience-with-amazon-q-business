# Common Errors
## InvalidGrantException:
This error indicates an issue while exchanging the token from the Identity Provider with IAM Identity Center application.
Some sources of error:
* User exists in web app directory (Cognito) but not in IAM Identity Center
* Trusted Token Issuer is misconfigured (attribute mapping or issuer URL). Be careful with trailing slashes as issuer must match with the Identity Provider. You can look at {issuerURL}/.well-known/openid-configuration to confirm the issuer URL.
* Customer Managed Application is misconfigured (audience)

## AccessDeniedException when calling CreateTokenWithIAM operation
This error indicates an issue while exchanging the token from the Identity Provider with IAM Identity Center application.
Some sources of error:
* User is not assigned to the customer managed application. You can either assign the users / groups to the customer managed application created or toggle the "Do not require assignments" option.
* The IAM role of the web application is not listed in the Application Credentials of the customer managed application in IAM Identity Center

## AccessDeniedException when calling the ChatSync operation
Some sources of error:
* User is not subscribed to the Q application. Hint: Look for `User is not authorized for this service call.` in the error message

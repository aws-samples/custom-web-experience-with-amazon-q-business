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

## Customer follows the blog to replicate the architecture/resoruces, however they observe a certificate error "not secure" in the browser when they try to access the application url. What is the root cause and how to resolve this issue.

Root Cauase analysis: A public valid certificate is provided from AWS certificate manager,  but there is a certificate error showing "not secure" in the browser. The resources creation is followed by the cloud formation template, and the created application url is a load balancer(LB) DNS name. The provided public certificate common name doesnot match load balancer DNS name, that is why there is the certificate error "not secure". 

In order to resolve this issue, please follow the steps below:
1. Please create a domain record from where you domain service is. Create the domain record which can be validated by your certificate uploaded in LB. For example, if your certificate is xyz.example.com, then you can create a domain record xyz.example.com points to the LB's DNS. If you are using Route53, the record can be A alias record or CName record, if you using other DNS service, it can be CName record.

2. Navigate to Amazon Cognito, choose User pools, then choose the user pool created by the cloud formation. Choose the tab App integration, and then scroll down to the bottom of the page to choose the App client. Click the App Client created by the cloud formation. Choose the Hosted UI, and chose Edit. Change the address for "Allowed callback URLs" and replace the LB DNS name to the custom domain name xyz.example.com in our case. The changed "Allowed callback URLs" will be https://xyz.example.com/component/streamlit_oauth.authorize_button/index.html for example.

3. Navigate to the AWS App Config service, choose the application created by cloud formation, and visit the Configuration profile details. Copy the profile content to the text editor of your choice. Notice that the value of "ExternalDns"  still points to the LB's DNS, and change it to the domain name xyz.example.com. And then click create, and copy paste the content from the text editor and then choose to "create hosted configuraiton version", then click the Start deployment button. This step will make sure that the application will start to use the created custom domain name instead of the DNS LB.

4. Test your custom UI by using the custom domain name instead of the LB's DNS, you should observe that the "not secure" error is gone. This is because the created custome domain that the user tries to access is matching the certificate's common name, so the domain name is validated by the certificate. 

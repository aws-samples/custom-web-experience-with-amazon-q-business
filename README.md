# Custom Web Experience with Amazon Q Business

Customers often want the ability to integrate custom functionalities into the Amazon Q user interface, such as handling feedback, using corporate colors and templates, custom login, and reducing context switching by integrating the user interface into a single platform. The code repo will show how to use Amazon cogntio for user authentication and use Amazon Q SDK to invoke chatbot application programmatically

<img src="docs/arch.jpg" alt="Architecture Diagram" width="400"/>


1.	First the user accesses the chatbot application, which is hosted behind the Load Balancer.
2.	On the first log in attempt the user is be redirected to the Amazon Cognito log in page for authentication. After successful authentication, the user is redirected back to the chatbot application.
3.	The custom UI, deployed on EC2, parses the token to obtain the user and group information, as well as the user's question. 
4.	The UI sends the above information to Amazon Q using the chat_sync boto3 API. AmazonQ return a response containing the answer and the sources used to generate it.


## Deploy this solution


### Prerequisites: 
Before you deploy this solution, make sure you have the following prerequisites set up:

- A valid AWS account.
- An AWS Identity and Access Management (IAM) role in the account that has sufficient permissions to create the necessary resources. If you have administrator access to the account, no action is necessary.
- An SSL certificate created and imported into AWS Certificate Manager (ACM). For more details, [refer to Importing a certificate](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-api-cli.html). If you do not have a public SSL certificate, follow the steps in the next section to learn how to generate a private certificate.
- An existing, working Amazon Q application 

### Generate Private certificate

If you already have an SSL certificate, you can skip this section.   
However, if you don't have one and want to proceed with running this demo, you can generate a private certificate associated with a domain using the following openssl command:
```
openssl req \
  -x509 -nodes -days 365 -sha256 \
  -subj '/C=US/ST=Oregon/L=Portland/CN=sampleexample.com' \
  -newkey rsa:2048 -keyout key.pem -out cert.pem

aws acm import-certificate --certificate fileb://cert.pem --private-key fileb://key.pem
```

Please note that, you will receive a warning from your browser when accessing the UI if you didn't provide a custom SSL certificate when launching the AWS CloudFormation Stack. Below instruction will show you how to create a self-signed certificate and used as a backup but this is certainly not recommended for production use cases. You should obtain an SSL Certificate that has been validated by a certificate authority, import it into AWS Certificate Manager and reference this when launching the AWS CloudFormation Stack. Should you wish to continue with the self-signed certificate (for development purposes), you should be able to proceed past the browser warning page. With Chrome, you will see a Your connection is not private error message (NET::ERR_CERT_AUTHORITY_INVALID), but by clicking on "Advanced" you should then see a link to proceed.


### Deploy this Solution: 

Step 1: Launch the AWS CloudFormation template. Launch the following AWS CloudFormation template to deploy ELB , Cognto User pool , including the EC2 instance to host the webapp. 


- Provide a Stack Name,
- And provide all the parameters for CloudFormation template .
- And copy the URL from the output tab once the stack is sucessfuly completed

<img src="docs/properties.png" alt="CloudFormation  parameters" width="400"/>



Step 2: Custom UI

The CloudFormation stack deploy and start the streamlit application on an EC2 instance on port 8080.On AWS console, we can navigate to EC2 then Load Balancing and under Target Groups, it shows the health of application running behind the Application Load Balancer. For any debugging purpose you can also connect to AWS EC2 through Session Manager. 

Connect to the EC2 through AWS Session Manager[Optional]: 

```
sudo su ec2-user
cd /home/ec2-user
ls
cd custom-web-experience-with-amazon-q-business/core
```
       

Step 3: Create a user account to login to the app 
-	On AWS Console navigate to Amazon Cognito page. 
-	Select the userpool that was created as part of cloudformation stack 
-	Click Create User
-	Enter user name, email, password and click Create User

Step 4: Update the Callback URL on Cognito
-	On AWS Console navigate to Amazon Cognito page. 
-	Select the userpool that was created as part of cloudformation stack   
-	Under the “App Integration” Tab > “App Client List” section > Select the client that was created 
-	On the Hosted UI section Click Edit 
-	Replace the text “replace_your_LB_url” with the URL that was copied from the cloudformation output tab in Step 1. Please convert the URL to Lowercase text if it’s not done already. 
-	Click Save Changes

Step 5: In a new browser window enter https://{url copied from step-1} and login using the username and password that was created in Step 5. Change the password if prompted.





## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.





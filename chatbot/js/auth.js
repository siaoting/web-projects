function test() {
    return "violet";
}
window.username = 'Unknown'
function initCognitoSDK() {
    var authData = {
            ClientId : '3h7hk1qpiilfmgpcf3lolov65i', // Your client id here
            AppWebDomain : '6998chatroom.auth.us-east-1.amazoncognito.com', // Exclude the "https://" part. 
            TokenScopesArray : ['openid','email'], // like ['openid','email','phone']...
            RedirectUriSignIn : 'https://s3.amazonaws.com/6998chatroom/index.html',
            RedirectUriSignOut : 'https://s3.amazonaws.com/6998chatroom/index.html',
            IdentityProvider : 'cognito-idp.us-east-1.amazonaws.com/us-east-1_wt15rIwSY', 
            UserPoolId : 'us-east-1_wt15rIwSY', 
            AdvancedSecurityDataCollectionFlag : false //<TODO: boolean value indicating whether you want to enable advanced security data collection>
    };
    AWS.config.update({region: 'us-east-1'});
    var auth = new AWSCognito.CognitoIdentityServiceProvider.CognitoAuth(authData);
    // You can also set state parameter 
    // auth.setState(<state parameter>);
    auth.userhandler = {
            onSuccess: function(result) {
                    console.log("Sign in success");
                    window.idToken = result.getIdToken().getJwtToken();
                    //console.log(idToken)
                    window.username = result.getAccessToken().getUsername()
                    AWS.config.credentials = new AWS.CognitoIdentityCredentials({
                        IdentityPoolId: "us-east-1:e457aadb-de01-459f-bf96-0f92ea1aad60",
                        Logins: {
                              'cognito-idp.us-east-1.amazonaws.com/us-east-1_wt15rIwSY': result.getIdToken().getJwtToken()
                        }
                    });

        	    //call refresh method in order to authenticate user and get new temp credentials
		    AWS.config.credentials.refresh((error) => {
			if (error) {
			    console.error(error);
			} else {
			    console.log('Successfully logged!');
			}
		    });

		    AWS.config.credentials.get(function() {
		        // Credentials will be available when this function is called.
		        window.accessKeyId = AWS.config.credentials.accessKeyId;
		        window.secretAccessKey = AWS.config.credentials.secretAccessKey;
		        window.sessionToken = AWS.config.credentials.sessionToken;
                        console.log("Get key success")
		    });
                    //console.log(auth.getCurrentUser())
                    //console.log(window["username"])
                    //showSignedIn(result);
            },
            onFailure: function(err) {
                console.log("Error!" + err);
                window.open('https://goo.gl/iszyc7','_self')
            }
    };
    // The default response_type is "token", uncomment the next line will make it be "code".
    // auth.useCodeGrantFlow();
    return auth;
}

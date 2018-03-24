var $chatlog = $('.js-chat-log');
var $input = $('.js-text');
var $sayButton = $('.js-say');
var dialogflowUrl = '{% url "index" %}';
var csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function createRow(text) {
    var $row = $('<li class="list-group-item"></li>');
    var list = '<li class="list-group-item">'
    var k = text.split("\n")

    for(i=0;i<k.length;i++) {
        list += k[i]+"<br />"
    }

    list = list + "</li>"
    $row.text(list);
    $chatlog.append(list);
}

createRow('<b><font size="4" face="Lucida Console">Chat with Robot</font></b>');

String.prototype.format = function() {
    a = this;
    for (k in arguments) {
        a = a.replace("{}", arguments[k])
    }
    return a
}

function submitInput() {
    // Enter user's unput
    var inputData = {
        'text': $input.val(),
        'username': window.username,
    }
    // Display the user's input on the web page
    createRow("<b>{}</b>: {}".format(inputData.username, inputData.text.trim()));
    $input.val('');

    var params = {"name":inputData["username"]};
    var body = {
      "messages": [
	{
	  "type": "string",
	  "unstructured": {
	    "id": "10001",
	    "text": inputData["text"],
	    "timestamp": "string"
	  }
	}
      ]
    };
    var additionalParams = ''
    var apigClient = apigClientFactory.newClient({
        accessKey: window.accessKeyId,
        secretKey: window.secretAccessKey,
        sessionToken: window.sessionToken, //OPTIONAL: If you are using temporary credentials you must include the session token
        region: 'us-east-1' // OPTIONAL: The region where the API is deployed, by default this parameter is set to us-east-1
    });
			
    apigClient.chatbotPost(params, body, additionalParams)
        .then(function(result) {
	    // Add success callback code here.
	    console.log("api success")
	    statement = result.data.messages[0].unstructured.text
	    createRow("<b>{}</b>: {}".format('Robot', statement));
	}).catch( function(result){
    	    // Add error callback code here.
    	    console.log(result)
    	    console.log("api fail")
	});
}

$sayButton.click(function() {
    submitInput();
});

$input.keydown(function(event) {
    // Submit the input when the enter button is pressed
    if (event.keyCode == 13) {
        submitInput();
    }
});


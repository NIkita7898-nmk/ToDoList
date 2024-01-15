email = document.querySelector('#email').value;
password = document.querySelector("#password").value;
// document.querySelector('#loginBtn').addEventListener('click', loginFunction(email, password));
document.querySelector('#loginBtn').addEventListener('click', function () {
    // Your action or function when the button is clicked
    console.log('Login button clicked!')
    email = document.querySelector('#email').value;
    password = document.querySelector("#password").value;
    console.log(email, password)
    result = loginFunction(email, password)
        .then(response => {
            console.log(response.access_token);
            console.log(response.refresh_token);
            // Use the tokens or handle the response as needed
        })
        .catch(error => {
            console.log(error);
            // Handle errors here
        });
});


async function loginFunction(email, password) {
    var raw = JSON.stringify({
        "email": email,
        "password": password
    });
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("Cookie", "csrftoken=AAceVkTfmocUdl33Um5wjdNwZqkrMxHjvmgIkQW52YHZab6Gsid8AkUC7lYaWS1g");

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };
    try {
        const response = await fetch("http://127.0.0.1:5000/login/", requestOptions);

        if (response.ok) {
            const result = await response.json();
            // Assuming result contains login information
            // Redirect to home page or perform actions for successful login
            window.location.href = "/home"; // Redirect to home page
        } else {
            // Handle bad request or other error responses
            console.warn('Bad request. Please check your credentials.');
        }
    } catch (error) {
        console.error('Error:', error);
        // Handle other errors (network issues, server problems, etc.)
    }
}



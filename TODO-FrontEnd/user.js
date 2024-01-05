

document.querySelector('#loginBtn').addEventListener('click', function () {
    // Your action or function when the button is clicked
    console.log('Login button clicked!')
    email = document.querySelector('#email').value;
    password = document.querySelector("#password").value;
    console.log(email, password)
    loginFunction(email, password)
});


function loginFunction(email, password) {
    console.log("login")
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

    fetch("http://127.0.0.1:5000/login/", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => console.log('error', error));
}
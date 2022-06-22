if (user != 'AnonymousUser'){
    document.getElementById('login-btn').classList.add("hidden");
}else{
    document.getElementById('hello-msg').classList.add("hidden");
    document.getElementById('logout-span').classList.add("hidden");
}
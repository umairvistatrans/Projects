$(document).ready(function () {
    var placeholder = document.getElementById('instagram-script-placeholder');
    if (placeholder) {
        var script = document.createElement('script');
        script.async = true;
        script.defer = true;
        script.src = "https://www.instagram.com/embed.js";
        placeholder.appendChild(script);
    } else {
        console.warn("Instagram script placeholder not found.");
    }
});
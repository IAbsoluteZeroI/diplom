document.addEventListener("DOMContentLoaded", function() {
    var dropdownBtns = document.querySelectorAll(".dropdown-btn");
    
    dropdownBtns.forEach(function(btn) {
        btn.addEventListener("click", function() {
            var dropdownContent = this.nextElementSibling;
            dropdownContent.classList.toggle("show");
        });
    });
});

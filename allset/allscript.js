document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector(".chat-toggle");
    const closeButton = document.querySelector(".chevron");
    const mainContent = document.querySelector("main");

    toggleButton.addEventListener("click", function () {
        if (!sidebar.classList.contains("expanded")) {
            sidebar.classList.add("expanded");
            mainContent.classList.add("shrink");
        } else {
            sidebar.classList.remove("expanded");
            mainContent.classList.remove("shrink");
        }
    });

    closeButton.addEventListener("click", function () {
        sidebar.classList.remove("expanded");
        mainContent.classList.remove("shrink");
    });
});


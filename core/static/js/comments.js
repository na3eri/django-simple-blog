document.addEventListener("DOMContentLoaded", function () {
    const replyButtons = document.querySelectorAll(".reply-btn");
    const parentInput = document.getElementById("id_parent_id");

    replyButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const commentId = this.dataset.commentId;

            parentInput.value = commentId;
        });
    });
});
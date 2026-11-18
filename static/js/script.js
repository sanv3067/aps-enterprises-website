document.addEventListener("DOMContentLoaded", function () {
    const enquiryForm = document.getElementById("enquiry-form");

    if (enquiryForm) {
        enquiryForm.addEventListener("submit", function () {
            const submitButton = enquiryForm.querySelector(
                'button[type="submit"]'
            );

            if (enquiryForm.checkValidity()) {
                submitButton.disabled = true;
                submitButton.textContent = "Submitting...";
            }
        });
    }
});
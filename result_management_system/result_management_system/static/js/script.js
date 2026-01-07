// Close alert messages
document.addEventListener('DOMContentLoaded', function() {
    // Close alert buttons
    const closeButtons = document.querySelectorAll('.close-alert');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
    
    // Grade preview for add result form
    const marksInput = document.getElementById('marks');
    const maxMarksInput = document.getElementById('max_marks');
    
    if (marksInput && maxMarksInput) {
        function updateGradePreview() {
            const marks = parseFloat(marksInput.value) || 0;
            const maxMarks = parseFloat(maxMarksInput.value) || 100;
            
            if (marks > maxMarks) {
                marksInput.value = maxMarks;
                updateGradePreview();
                return;
            }
        }
        
        marksInput.addEventListener('input', updateGradePreview);
        maxMarksInput.addEventListener('input', updateGradePreview);
    }
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e74c3c';
                    field.focus();
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Add active class to current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
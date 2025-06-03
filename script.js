document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientForm');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const accordion = document.getElementById('analysisAccordion');

    // Save form data to localStorage when input changes
    const formInputs = form.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            localStorage.setItem(input.id, input.value);
        });
        
        // Load saved data if exists
        const savedValue = localStorage.getItem(input.id);
        if (savedValue) {
            input.value = savedValue;
        }
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        loadingDiv.classList.remove('d-none');
        resultsDiv.classList.add('d-none');
        accordion.innerHTML = '';

        // Disable the submit button while processing
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';

        // Prepare the patient data
        const patientData = {
            text: `Patient Name: ${document.getElementById('patientName').value}\n` +
                  `Age: ${document.getElementById('age').value}\n` +
                  `Symptoms: ${document.getElementById('symptoms').value}\n` +
                  `Medical History: ${document.getElementById('medicalHistory').value || 'None'}\n` +
                  `Allergies: ${document.getElementById('allergies').value || 'None'}\n` +
                  `Current Medications: ${document.getElementById('currentMedications').value || 'None'}`
        };

        try {
            // Call the API
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patientData)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Process each agent's response
            data.forEach((result, index) => {
                const content = result.response.content;
                const text = content.text.split('\n');
                
                // Create accordion item
                const accordionItem = document.createElement('div');
                accordionItem.className = 'accordion-item';
                
                // Determine title and icon based on agent type
                let title = '';
                let icon = '';
                switch(result.agent_type) {
                    case 'patient_info':
                        title = 'Patient Information';
                        icon = '👤';
                        break;
                    case 'diagnostic':
                        title = 'Diagnostic Analysis';
                        icon = '🏥';
                        break;
                    case 'medication':
                        title = 'Medication Suggestions';
                        icon = '💊';
                        break;
                    case 'referral_diet':
                        title = 'Referral & Diet Recommendations';
                        icon = '🍎';
                        break;
                }

                // Create accordion header
                accordionItem.innerHTML = `
                    <h2 class="accordion-header" id="heading${index}">
                        <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" 
                                type="button" 
                                data-bs-toggle="collapse" 
                                data-bs-target="#collapse${index}">
                            ${icon} ${title}
                        </button>
                    </h2>
                    <div id="collapse${index}" 
                         class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                         data-bs-parent="#analysisAccordion">
                        <div class="accordion-body">
                            ${text.map(line => {
                                // Add special formatting for warnings and recommendations
                                if (line.includes('CAUTION:') || line.includes('URGENT:')) {
                                    return `<div class="alert alert-danger">${line}</div>`;
                                } else if (line.includes('Recommendation:')) {
                                    return `<div class="recommendation">${line}</div>`;
                                } else if (line.trim().length > 0) {
                                    return `<p>${line}</p>`;
                                }
                                return '';
                            }).join('')}
                        </div>
                    </div>
                `;
                
                accordion.appendChild(accordionItem);
            });

            // Show results
            loadingDiv.classList.add('d-none');
            resultsDiv.classList.remove('d-none');

        } catch (error) {
            console.error('Error:', error);
            accordion.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error Processing Request</h5>
                    <p>An error occurred while processing your request. Please check if all services are running:</p>
                    <ul>
                        <li>Patient Info Agent (Port 5001)</li>
                        <li>Diagnostic Agent (Port 5002)</li>
                        <li>Medication Agent (Port 5003)</li>
                        <li>Referral & Diet Agent (Port 5004)</li>
                    </ul>
                </div>
            `;
            loadingDiv.classList.add('d-none');
            resultsDiv.classList.remove('d-none');
        } finally {
            // Re-enable the submit button
            submitButton.disabled = false;
            submitButton.innerHTML = 'Analyze';
        }
    });

    // Add a clear form button
    const clearButton = document.createElement('button');
    clearButton.type = 'button';
    clearButton.className = 'btn btn-secondary ms-2';
    clearButton.innerHTML = 'Clear Form';
    clearButton.onclick = function() {
        form.reset();
        localStorage.clear();
        accordion.innerHTML = '';
    };
    form.querySelector('button[type="submit"]').after(clearButton);
}); 
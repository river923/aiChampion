document.addEventListener('DOMContentLoaded', function() {
    const providerSelect = document.querySelector('select[name="provider"]');
    const modelNameInput = document.querySelector('input[name="model_name"]');

    if (!providerSelect || !modelNameInput) return;

    // Create datalist element
    let datalist = document.getElementById('openrouter-models');
    if (!datalist) {
        datalist = document.createElement('datalist');
        datalist.id = 'openrouter-models';
        document.body.appendChild(datalist);
    }

    async function fetchModels() {
        if (providerSelect.value === 'openrouter') {
            modelNameInput.setAttribute('list', 'openrouter-models');
            if (datalist.children.length === 0) {
                try {
                    const response = await fetch('https://openrouter.ai/api/v1/models');
                    const data = await response.json();
                    data.data.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.id;
                        option.textContent = model.name;
                        datalist.appendChild(option);
                    });
                } catch (e) {
                    console.error("Failed to fetch OpenRouter models", e);
                }
            }
        } else {
            modelNameInput.removeAttribute('list');
        }
    }

    providerSelect.addEventListener('change', fetchModels);
    // Fetch immediately if already openrouter
    fetchModels();
});

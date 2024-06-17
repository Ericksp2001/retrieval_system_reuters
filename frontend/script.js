document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const searchOptions = document.querySelectorAll('input[name="search-method"]');
    const errorMessage = document.getElementById('error-message');
    const searchForm = document.getElementById('search-form');
    const queryInput = document.getElementById('query-input');
    const resultadosContainer = document.getElementById('resultados-container');

    searchOptions.forEach(option => {
        option.addEventListener('change', () => {
            if (document.querySelector('input[name="search-method"]:checked')) {
                searchButton.disabled = false;
                errorMessage.style.display = 'none';
            }
        });
    });

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const selectedOption = document.querySelector('input[name="search-method"]:checked');
        
        if (!selectedOption) {
            errorMessage.style.display = 'block';
            return;
        }

        const query = queryInput.value; 

        if (!query) {
            errorMessage.textContent = 'Por favor ingrese una consulta en la barra de búsqueda';
            errorMessage.style.display = 'block';
            return;
        }

        errorMessage.style.display = 'none';

        enviarSolicitudAPI(query);
    });

    function enviarSolicitudAPI(query) {
        const apiUrl = 'http://127.0.0.1:5000/process';
        const selectedOption = document.querySelector('input[name="search-method"]:checked');
        let tv, tr;
    
        if (selectedOption) {
            if (selectedOption.value === 'tfidf-cosine') {
                tv = 0;
                tr = 1;
            } else if (selectedOption.value === 'bow-jaccard') {
                tv = 1;
                tr = 0;
            }
        }
    
        const datos = { query: query, tv: tv, tr: tr };
    
        const opciones = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        };
    
        fetch(apiUrl, opciones)
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Error al comunicarse con la API');
            })
            .then(data => {
                console.log(data);
                mostrarResultados(data.result.trim());
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                // Resetear el formulario y las opciones de búsqueda
                searchForm.reset();
                searchButton.disabled = true;
                queryInput.value = ''; // Limpiar el valor de la barra de búsqueda
                searchOptions.forEach(option => {
                    option.checked = false; // Desmarcar todas las opciones de búsqueda
                });
            });
    }

    function mostrarResultados(resultados) {
        resultadosContainer.innerHTML = ''; // Limpiar resultados anteriores
    
        // Extraer los nombres de archivos de la cadena
        const archivos = resultados.replace(/[\[\]']/g, '').split(', ');
    
        if (archivos.length === 0 || (archivos.length === 1 && archivos[0] === '')) {
            const noResultsMessage = document.createElement('div');
            noResultsMessage.textContent = 'No se encontraron resultados.';
            noResultsMessage.classList.add('no-results-message');
            resultadosContainer.appendChild(noResultsMessage);
        } else {
            const resultadosDiv = document.createElement('div');
            resultadosDiv.classList.add('resultados');
            
            const titleElement = document.createElement('h3');
            titleElement.textContent = 'Documentos:';
            resultadosDiv.appendChild(titleElement);
            
            const documentosElement = document.createElement('p');
            documentosElement.textContent = archivos.join(', ');
            resultadosDiv.appendChild(documentosElement);
    
            resultadosContainer.appendChild(resultadosDiv);
        }
    }
});

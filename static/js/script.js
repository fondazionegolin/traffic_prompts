document.addEventListener('DOMContentLoaded', function() {
    let state = {
        gender: '',
        age: '',
        infanzia: [],
        maturita: [],
        vecchiaia: [],
        maxSelectionsPerPhase: 3
    };

    // Carica lo stato iniziale dai bottoni già selezionati
    function loadInitialState() {
        // Carica genere
        const selectedGender = document.querySelector('.gender-btn.selected');
        if (selectedGender) {
            state.gender = selectedGender.dataset.gender;
        }

        // Carica età
        const selectedAge = document.querySelector('.age-btn.selected');
        if (selectedAge) {
            state.age = selectedAge.dataset.age;
        }

        // Carica parole selezionate
        document.querySelectorAll('.word-btn.selected').forEach(btn => {
            const phase = btn.dataset.phase;
            const word = btn.dataset.word;
            if (phase && word) {
                if (!state[phase]) state[phase] = [];
                state[phase].push(word);
            }
        });

        console.log('Stato iniziale caricato:', state);
        checkCompleteness();
    }

    function updateHeader(isComplete) {
        const header = document.getElementById('status-indicator');
        const waitingMsg = document.querySelector('.waiting-message');
        const readyMsg = document.querySelector('.ready-message');

        if (isComplete) {
            header.style.backgroundColor = '#00ff00';
            header.style.boxShadow = '0 0 15px #00ff00';
            waitingMsg.style.display = 'none';
            readyMsg.style.display = 'block';
        } else {
            header.style.backgroundColor = '#ff0000';
            header.style.boxShadow = '0 0 15px #ff0000';
            waitingMsg.style.display = 'block';
            readyMsg.style.display = 'none';
        }
    }

    function showSuccessOverlay() {
        const overlay = document.querySelector('.success-overlay');
        const codeValue = document.querySelector('.code-value').textContent;
        document.querySelector('.code-value-large').textContent = codeValue;
        overlay.classList.add('show');
        
        // Reset dopo 5 secondi
        setTimeout(() => {
            overlay.classList.remove('show');
            location.reload();
        }, 5000);
    }

    function checkCompleteness() {
        const isComplete = 
            state.gender !== '' &&
            state.age !== '' &&
            state.infanzia.length === 3 &&
            state.maturita.length === 3 &&
            state.vecchiaia.length === 3;

        if (isComplete) {
            saveData().then(() => {
                showSuccessOverlay();
            });
        }

        console.log('Stato corrente:', {
            gender: state.gender,
            age: state.age,
            infanzia: state.infanzia.length + '/3',
            maturita: state.maturita.length + '/3',
            vecchiaia: state.vecchiaia.length + '/3',
            isComplete: isComplete
        });

        updateHeader(isComplete);
        return isComplete;
    }

    // Gestione click sui bottoni del sesso
    document.querySelectorAll('.gender-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all gender buttons
            document.querySelectorAll('.gender-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            
            // Add selected class to clicked button
            this.classList.add('selected');
            
            // Update state
            state.gender = this.dataset.gender;
            
            checkCompleteness();
        });
    });

    // Gestione click sui bottoni dell'età
    document.querySelectorAll('.age-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all age buttons
            document.querySelectorAll('.age-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            
            // Add selected class to clicked button
            this.classList.add('selected');
            
            // Update state
            state.age = this.dataset.age;
            
            checkCompleteness();
        });
    });

    // Gestione click sulle parole
    document.querySelectorAll('.word-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const phase = btn.dataset.phase;
            const word = btn.dataset.word;

            if (!phase || !word) return;

            if (btn.classList.contains('selected')) {
                btn.classList.remove('selected');
                state[phase] = state[phase].filter(w => w !== word);
            } else {
                if (state[phase].length < 3) {
                    btn.classList.add('selected');
                    state[phase].push(word);
                }
            }

            checkCompleteness();
        });
    });

    function saveData() {
        const data = {
            codice: document.querySelector('.code-value').textContent,
            sesso: state.gender,
            eta: state.age,
            infanzia: state.infanzia,
            maturita: state.maturita,
            vecchiaia: state.vecchiaia
        };

        return fetch('/save_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Salvato:', data);
            return data;
        })
        .catch(error => {
            console.error('Errore:', error);
            throw error;
        });
    }

    // Inizializza lo stato
    loadInitialState();
});

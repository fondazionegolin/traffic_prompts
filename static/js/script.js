document.addEventListener('DOMContentLoaded', function() {
    let selectedGender = null;
    let selectedAge = null;
    const selectedWords = {
        infanzia: [],
        maturita: [],
        vecchiaia: []
    };

    const userCodeSection = document.querySelector('.user-code-section');
    const userCode = document.querySelector('.code').textContent.trim();

    // Gender selection
    document.querySelectorAll('.gender-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            selectedGender = this.dataset.gender;
            checkSelections();
        });
    });

    // Age selection
    document.querySelectorAll('.age-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.age-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            selectedAge = this.dataset.age;
            checkSelections();
        });
    });

    // Word selection
    document.querySelectorAll('.word-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const phase = this.dataset.phase;
            const word = this.textContent.trim();

            if (this.classList.contains('selected')) {
                // Deselect word
                this.classList.remove('selected');
                selectedWords[phase] = selectedWords[phase].filter(w => w !== word);
                checkSelections();
            } else {
                // Only select if less than 3 words are selected for this phase
                if (selectedWords[phase].length < 3) {
                    this.classList.add('selected');
                    selectedWords[phase].push(word);
                    checkSelections();
                }
            }
        });
    });

    function saveUserData() {
        const userData = {
            codice: userCode,
            sesso: selectedGender,
            eta: selectedAge,
            infanzia: selectedWords.infanzia,
            maturita: selectedWords.maturita,
            vecchiaia: selectedWords.vecchiaia,
            timestamp: new Date().toISOString()
        };

        fetch('/save_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function checkSelections() {
        // Check if gender is selected
        if (!selectedGender) {
            userCodeSection.classList.remove('status-green');
            userCodeSection.classList.add('status-red');
            return;
        }

        // Check if age is selected
        if (!selectedAge) {
            userCodeSection.classList.remove('status-green');
            userCodeSection.classList.add('status-red');
            return;
        }

        // Check if exactly 3 words are selected for each phase
        const isComplete = 
            selectedWords.infanzia.length === 3 &&
            selectedWords.maturita.length === 3 &&
            selectedWords.vecchiaia.length === 3;

        if (isComplete) {
            userCodeSection.classList.remove('status-red');
            userCodeSection.classList.add('status-green');
            
            // Save data and reset after successful save
            saveUserData();
        } else {
            userCodeSection.classList.remove('status-green');
            userCodeSection.classList.add('status-red');
        }
    }

    // Initial check
    checkSelections();
});

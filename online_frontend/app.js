document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. SCROLL REVEAL ANIMATIONS ---
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15 
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    revealElements.forEach(el => observer.observe(el));

    // --- 2. ACTIVE NAVIGATION HIGHLIGHTING ---
    const sections = document.querySelectorAll('section.page-section');
    const navLinks = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - sectionHeight / 3)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').includes(current)) {
                link.classList.add('active');
            }
        });
    });

    // --- 3. CTA BUTTON SCROLL TO SEARCH ---
    const ctaBtn = document.getElementById('cta-search-btn');
    const searchSection = document.getElementById('search-section');
    const queryInput = document.getElementById('query-input');

    if (ctaBtn && searchSection && queryInput) {
        ctaBtn.addEventListener('click', () => {
            searchSection.scrollIntoView({ behavior: 'smooth' });
            setTimeout(() => { queryInput.focus(); }, 2500);
        });
    }

    // --- 5. TEAM CAROUSEL LOGIC (Bulletproof Loop) ---
    // MOVED OUTSIDE OF SEARCH LOGIC so it runs on about.html
    const track = document.getElementById('carousel-track');
    
    if (track) {
        const slides = Array.from(document.querySelectorAll('.carousel-slide'));
        const indicators = Array.from(document.querySelectorAll('.indicator'));
        
        let currentSlide = 0;
        const slideDuration = 6000;
        let carouselTimer;

        function goToSlide(index) {
            // Remove active classes
            slides.forEach(slide => slide.classList.remove('active'));
            indicators.forEach(ind => {
                ind.classList.remove('active');
                void ind.offsetWidth; // Force CSS animation restart
            });

            // Update index
            currentSlide = index;
            
            // Add active classes
            slides[currentSlide].classList.add('active');
            indicators[currentSlide].classList.add('active');
            track.style.transform = `translateX(-${currentSlide * 100}%)`;
            
            // Reset the timer so it doesn't double-trigger
            clearInterval(carouselTimer);
            carouselTimer = setInterval(nextSlide, slideDuration);
        }

        function nextSlide() {
            // The modulo (%) ensures it safely loops back to 0 when it hits the end
            let nextIndex = (currentSlide + 1) % slides.length;
            goToSlide(nextIndex);
        }

        // Allow manual clicking
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => goToSlide(index));
        });

        // Jumpstart the automatic loop on page load
        clearInterval(carouselTimer);
        carouselTimer = setInterval(nextSlide, slideDuration);
    }

    // --- 6. SCROLL TO TOP ARROW LOGIC ---
    // MOVED OUTSIDE OF SEARCH LOGIC so it runs on all pages
    const scrollTopBtn = document.getElementById('scroll-to-top');
    
    if (scrollTopBtn) {
        // Show/hide the button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) { // Shows up after scrolling down 400px
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });

        // Scroll back up smoothly when clicked
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }


    // --- 4. SEARCH LOGIC (Backend Connection) ---
    const searchBtn = document.getElementById('search-btn');
    
    // Added safety check so search logic only runs on the page with a search bar
    if (searchBtn && queryInput) {
        searchBtn.addEventListener('click', handleSearch);
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });

        let loaderInterval; // Variable to hold our loading text timer

        async function handleSearch() {
            const query = queryInput.value.trim();
            const court = document.getElementById('court-filter').value.trim();
            const jurisdiction = document.getElementById('jurisdiction-filter').value.trim();
            const judge = document.getElementById('judge-filter').value.trim();
            
            if (!query) return;

            // Reset UI
            document.getElementById('results-container').classList.remove('hidden');
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results-output').innerHTML = '';

            // Dynamic Pipeline Loader Text
            const loaderText = document.getElementById('loader-text');
            const pipelineSteps = [
                "Vectorizing query embedding...",
                "Searching FAISS index...",
                "Filtering SQLite metadata...",
                "Running Cross-Encoder reranking...",
            ];
            let stepIndex = 0;
            
            // Cycle text every 800ms
            loaderText.innerText = pipelineSteps[0];
            loaderInterval = setInterval(() => {
                stepIndex = (stepIndex + 1) % pipelineSteps.length;
                loaderText.innerText = pipelineSteps[stepIndex];
            }, 800);

            try {
                // Actual local endpoint
                //const response = await fetch('http://127.0.0.1:8000/search', {
                const response = await fetch('https://defeat-sessions-slip.ngrok-free.dev/search', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        court: court || null,
                        jurisdiction: jurisdiction || null,
                        judge: judge || null
                    })
                });

                const data = await response.json();
                
                // Clean up loader
                clearInterval(loaderInterval);
                document.getElementById('loading').classList.add('hidden');
                
                renderRealResults(data.results); 
            } catch (error) {
                console.error("Search failed:", error);
                clearInterval(loaderInterval);
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('results-output').innerHTML = 
                    "<p style='color:red'>Backend error. Please check if your FastAPI server is running.</p>";
            }
        }

        function renderRealResults(results) {
            const resultsOutput = document.getElementById('results-output');
            resultsOutput.innerHTML = ''; 

            if (!results || results.length === 0) {
                resultsOutput.innerHTML = "<p>No results found for your query.</p>";
                return;
            }

            results.forEach((res, index) => {
                const card = document.createElement('div');
                card.className = 'result-card';
                
                // STAGGERED ANIMATION DELAY: Each card waits 0.1s longer than the previous one
                card.style.animationDelay = `${index * 0.1}s`;
                
                const analysis = res.analysis || {};
                const categoryName = analysis.category || 'Uncategorized';

                const createBlock = (label, text) => text ? 
                    `<span class="legal-label">${label}</span><div class="legal-text">${text}</div>` : '';

                card.innerHTML = `
                    <h3>${index + 1}. ${res.case_metadata.title}</h3>
                    <div class="result-meta">
                        ${res.case_metadata.court} • ${res.case_metadata.decision_year} • 
                        <strong>Category:</strong> ${categoryName}
                    </div>
                    
                    <div class="hover-summary">
                        <strong>Legal Issue:</strong><br>${analysis.legal_issue || 'Not explicitly stated.'}
                    </div>

                    <div class="expanded-content" id="expanded-${index}">
                        <div class="summary-box">
                            <span class="legal-label">Full Case Summary</span>
                            <div class="legal-text">${res.summary || 'No summary available.'}</div>
                        </div>
                        <div class="analysis-box">
                            ${createBlock("Legal Issue", analysis.legal_issue)}
                            ${createBlock("Holding", analysis.holding)}
                            ${createBlock("Reasoning", analysis.reasoning)}
                            ${createBlock("Procedural Posture", analysis.procedural_posture)}
                        </div>
                    </div>
                `;

                card.addEventListener('click', (e) => {
                    const expanded = card.querySelector('.expanded-content');
                    const preview = card.querySelector('.hover-summary');
                    
                    const isOpen = expanded.classList.toggle('open');
                    
                    if (isOpen) {
                        preview.classList.add('preview-hidden'); 
                        setTimeout(() => {
                            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }, 300);
                    } else {
                        preview.classList.remove('preview-hidden'); 
                    }
                });

                resultsOutput.appendChild(card);
            });
        }
    }
});

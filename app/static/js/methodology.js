// Add this new file for methodology-specific JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Component cards hover effect
    const cards = document.querySelectorAll('.component-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('transform', 'scale-105', 'transition-all', 'duration-200');
        });
        card.addEventListener('mouseleave', () => {
            card.classList.remove('transform', 'scale-105');
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add table of contents navigation
    const toc = document.createElement('nav');
    toc.className = 'fixed right-4 top-1/4 hidden lg:block z-50';
    toc.innerHTML = `
        <div class="bg-gray-800 rounded-lg p-4 shadow-lg">
            <h3 class="text-sm font-semibold mb-2 text-eth-blue">On this page</h3>
            <ul class="space-y-2 text-sm">
                <li><a href="#overview" class="toc-link text-gray-300 hover:text-white">Overview</a></li>
                <li><a href="#formulas" class="toc-link text-gray-300 hover:text-white">Formula Comparison</a></li>
                <li><a href="#components" class="toc-link text-gray-300 hover:text-white">Components</a></li>
                <li><a href="#why-matters" class="toc-link text-gray-300 hover:text-white">Why This Matters</a></li>
                <li><a href="#projections" class="toc-link text-gray-300 hover:text-white">Growth Potential</a></li>
            </ul>
        </div>
    `;
    document.body.appendChild(toc);

    // Add intersection observer for sections
    const sections = document.querySelectorAll('section[id]');
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                document.querySelectorAll('.toc-link').forEach(link => {
                    link.classList.remove('text-eth-blue');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('text-eth-blue');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));

    // Add active state to current section on scroll
    window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollPosition >= sectionTop - 100 && scrollPosition < sectionTop + sectionHeight - 100) {
                const id = section.getAttribute('id');
                document.querySelectorAll('.toc-link').forEach(link => {
                    link.classList.remove('text-eth-blue');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('text-eth-blue');
                    }
                });
            }
        });
    });
}); 
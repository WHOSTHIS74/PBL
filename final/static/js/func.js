// Smooth scroll for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Smooth scroll for the "scroll-down" button
document.querySelector('.scroll-down').addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector('#introduction').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
});

// Fade-in effect on scroll
const sections = document.querySelectorAll('section');
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1 });

sections.forEach(section => observer.observe(section));

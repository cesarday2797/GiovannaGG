const draggables = document.querySelectorAll('.draggable');
const dropzone = document.querySelector('.dropzone');

draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', () => {
        draggable.classList.add('dragging');
    });

    draggable.addEventListener('dragend', () => {
        draggable.classList.remove('dragging');
    });
});

dropzone.addEventListener('dragover', e => {
    e.preventDefault();
});

dropzone.addEventListener('drop', e => {
    e.preventDefault();
    const draggable = document.querySelector('.dragging');
    dropzone.appendChild(draggable);
});

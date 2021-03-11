function rotateArrow(arrowId) {
    // toggle the rotation of the arrow button based on previous rotation
    let arrow = document.getElementById(arrowId).style.transform;
    if (arrow === 'rotate(270deg)') {
        arrow = "rotate(0deg)";
    } else {
        arrow = "rotate(270deg)";
    }
    document.getElementById(arrowId).style.transform = arrow;
}
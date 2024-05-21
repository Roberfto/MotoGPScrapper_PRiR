document.addEventListener("DOMContentLoaded", function() {
    const backgrounds = [
        'https://images2.alphacoders.com/130/thumb-1920-1308982.jpeg',
        'https://images3.alphacoders.com/132/thumb-1920-1324581.png',
        //'https://resources.motogp.pulselive.com/photo-resources/2023/11/23/cb186c2d-4956-4e77-be3b-da3a90466bbd/RSM.jpg?height=465&width=1440',
        //'https://resources.motogp.pulselive.com/photo-resources/2023/11/23/bd9e6b1c-17d0-450c-9259-80b9f6a5d138/GBR.jpg?height=465&width=1440',

    ];

    let currentBackground = 0;

    function changeBackground() {
        document.body.style.backgroundImage = `url('${backgrounds[currentBackground]}')`;
        currentBackground = (currentBackground + 1) % backgrounds.length;
        setTimeout(changeBackground, 45000); // Zmiana tła co 1 minuty (60000 ms)
    }

    setTimeout(changeBackground, 45000);
});

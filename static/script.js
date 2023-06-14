function redirectToRoute(data) {
    const encodedData = encodeURIComponent(data);
    const url = "/item/" + encodedData;
    window.location.href = url;
}

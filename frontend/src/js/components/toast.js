export function showToast(message) {

    const toast = document.createElement("div");

    toast.className =
        "fixed bottom-6 right-6 bg-gray-900 text-white px-4 py-2 rounded-lg shadow-md";

    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);

}
document.addEventListener("DOMContentLoaded", function () {

    const inputs = document.querySelectorAll('input[type="file"]');

    inputs.forEach(input => {

        const container = document.createElement("div");
        container.className = "file-preview-container";

        input.parentNode.appendChild(container);

        input.addEventListener("change", function () {

            container.innerHTML = "";

            const files = Array.from(input.files);

            files.forEach((file, index) => {

                if (!file.type.startsWith("image/")) return;

                const reader = new FileReader();

                reader.onload = function (e) {

                    const wrapper = document.createElement("div");
                    wrapper.className = "preview-item";

                    const img = document.createElement("img");
                    img.src = e.target.result;

                    const remove = document.createElement("button");
                    remove.innerText = "✖";
                    remove.className = "preview-remove";

                    remove.onclick = function () {

                        const dt = new DataTransfer();

                        files
                            .filter((_, i) => i !== index)
                            .forEach(f => dt.items.add(f));

                        input.files = dt.files;
                        input.dispatchEvent(new Event("change"));

                    };

                    wrapper.appendChild(img);
                    wrapper.appendChild(remove);

                    container.appendChild(wrapper);

                };

                reader.readAsDataURL(file);

            });

        });

    });

});
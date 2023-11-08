class TableCsv {
    /**
     * @param {HTMLTableElement} root The table element which will display the CSV data.
     */
    constructor(root) {
      this.root = root;
    }
  
    /**
     * Clears existing data in the table and replaces it with new data.
     *
     * @param {string[][]} data A 2D array of data to be used as the table body
     * @param {string[]} headerColumns List of headings to be used
     */
    update(data, headerColumns = []) {
      this.clear();
      this.setHeader(headerColumns);
      this.setBody(data);
    }
  
    /**
     * Clears all contents of the table (incl. the header).
     */
    clear() {
      this.root.innerHTML = "";
    }
  
    /**
     * Sets the table header.
     *
     * @param {string[]} headerColumns List of headings to be used
     */
    setHeader(headerColumns) {
      this.root.insertAdjacentHTML(
        "afterbegin",
        `
              <thead>
                  <tr>
                      ${headerColumns.map((text) => `<th>${text}</th>`).join("")}
                  </tr>
              </thead>
          `
      );
    }
  
    /**
     * Sets the table body.
     *
     * @param {string[][]} data A 2D array of data to be used as the table body
     */
    setBody(data) {
      const rowsHtml = data.map((row) => {
        return `
                  <tr>
                      ${row.map((text) => `<td>${text}</td>`).join("")}
                  </tr>
              `;
      });
  
      this.root.insertAdjacentHTML(
        "beforeend",
        `
              <tbody>
                  ${rowsHtml.join("")}
              </tbody>
          `
      );
    }
  }
  
  const tableRoot = document.querySelector("#csvRoot");
  const csvFileInput = document.getElementById("file");
  const tableCsv = new TableCsv(tableRoot);
  
  csvFileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    const label = document.getElementById('datasetname');
    label.innerHTML = file.name;
    Papa.parse(file, {
      delimiter: ",",
      skipEmptyLines: true,
      complete: (results) => {
        tableCsv.update(results.data.slice(1), results.data[0]);
      }
    });
  });
  
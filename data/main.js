const fs = require('fs')

fs.readFile('stock.txt', 'utf8', function (err, data) {
    if (err) {
        return console.log(err);
    }
    var data_arr = data.split(/\s* \s*/)
    const json = {}


    while (data_arr.length) {
        let i = 1
        const sector = {}
        while (parseInt(data_arr[i])) {
            sector[data_arr[i]] = data_arr[i + 1]
            i += 2
        }
        if (json[data_arr[0].toString()] == undefined)
            json[data_arr[0].toString()] = sector
        else
            json[data_arr[0].toString() + '_'] = sector
        // console.log(data_arr[i - 1])
        data_arr = data_arr.slice(i)
    }

    console.log(json)
    // console.log(json)
    fs.writeFile('stock_list.json', JSON.stringify(json), 'utf8', function (err2) {
        if (err2) throw err2;
    });
});
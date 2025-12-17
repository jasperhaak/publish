This is a test.


Font used to be:

```
      typography: {
        header: "Schibsted Grotesk",
        body: "Source Sans Pro",
        code: "IBM Plex Mono",
      },
```

Changed to:

```
typography: {
  header: "Bitter", // Usually fine as a string for headers
  body: {
    name: "Bitter",
    weights: [400, 600, 700], // 400 is regular, 700 is bold
    includeItalic: true,
  },
  code: "IBM Plex Mono",
},
```

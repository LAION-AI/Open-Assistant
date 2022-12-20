const poster = (url, { arg }) => {
  return fetch(url, {
    method: "POST",
    body: JSON.stringify(arg),
  });
};

export default poster;

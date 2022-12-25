import axios from "axios";

/**
 * A minimal Axios based fetcher.
 */
const fetcher = (url) => axios.get(url).then((res) => res.data);

export default fetcher;

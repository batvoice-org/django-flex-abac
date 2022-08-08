import axios from 'axios'
import { exampleappBaseURL } from '@/app.config';

// TODO: make DRY vs. api.service.js

class ExampleApiService {
  constructor() {
     this.instance = axios.create({
      baseURL: exampleappBaseURL
    })
  }

  removeHeader() {
    this.instance.defaults.headers.common = {}
  }

  request(method, url, data = {}, config = {}) {
    //config = {...config, params: {...config.params, as_user: "root"}}

    return this.instance({
      method,
      url,
      data,
      ...config
    })
  }

  get(url, config = {}) {
    return this.request('GET', url, {}, config)
  }

  post(url, data, config = {}) {
    return this.request('POST', url, data, config)
  }

  put(url, data, config = {}) {
    return this.request('PUT', url, data, config)
  }

  patch(url, data, config = {}) {
    console.log("data", data)
    return this.request('PATCH', url, data, config)
  }

  delete(url, config = {}) {
    return this.request('DELETE', url, {}, config)
  }
}

export default new ExampleApiService()

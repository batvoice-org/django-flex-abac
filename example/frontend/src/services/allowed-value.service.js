import ExampleApiService from '@/services/exampleapi.service'

class AllowedValueService {
  constructor() {
    this.request = ExampleApiService
  }

  list(username,/* model_names*/) {
    return this.request.get(
        `/exampleapp/get_all_allowed_values_per_user/`,
        {
            params: {
                'models': 'exampleapp.document',
                'as_user': username,
            }
        }
    )
  }
}

export default new AllowedValueService()

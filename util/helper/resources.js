import { fetch_meta } from "../fetch/meta"
import { get_schemas } from "./fetch_methods"
import { objectMatch } from "../objectMatch"
import { makeTemplate } from "../makeTemplate"


export const iconOf = {
  'CREEDS': `static/images/creeds.png`,
  'CMAP': `static/images/clueio.ico`,
}

const default_schemas = []

export async function get_library_resources() {
  // fetch schemas if missing
  const schemas = await get_schemas("/dcic/signature-commons-schema/v5/meta/schema/ui-schema.json")
  // fetch resources on database
  const { response } = await fetch_meta({
    endpoint: '/resources',
  })

  // fetch libraries on database
  const { response: libraries } = await fetch_meta({
    endpoint: '/libraries',
  })

  const resource_meta = response.filter((resource) => !resource.meta.$hidden).reduce((group, data) => {
    group[data.id] = data
    return group
  }, {})
  const resources_id = {}
  const resources = libraries.reduce((acc, lib) => {
    let resource_name
    let icon_src
    const resource_id = lib.resource
    // lib resource matches with resource table
    if (resource_id) {
      if (resource_id in resource_meta) {
        const resource = resource_meta[resource_id]
        // find matched schema 
        let matched_schemas = schemas.filter(
            (schema) => objectMatch(schema.match, resource)
        )
        if (matched_schemas.length === 0){
          matched_schemas = default_schemas.filter(
            (schema) => objectMatch(schema.match, resource)
          )
        }
        if (matched_schemas.length < 1) {
          console.error('Could not match ui-schema for', resource)
          return null
        }
        let name_prop = Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].name)
        if (name_prop.length > 0){
          resource_name = makeTemplate(matched_schemas[0].properties[name_prop[0]].text, resource)
        } else {
          console.warn('source of resource name is not defined, using either Resource_Name or ids')
          resource_name = resource.meta['Resource_Name'] || resource_id
        }

        let icon_prop =Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].icon)

        if (icon_prop.length > 0){
          icon_src = makeTemplate(matched_schemas[0].properties[icon_prop[0]].src, resource)
          icon_src = icon_src === 'undefined' ? `${process.env.PREFIX}/static/images/default-black.png`: icon_src
        } else {
          console.warn('source of lib icon is not defined, using default')
          icon_src = 'static/images/default-black.png'
        }
        if (!(resource_name in acc)) {
          resource.libraries = []
          resource.meta.icon = icon_src || `${process.env.PREFIX}/${resource.meta.icon}`
          acc[resource_name] = resource
        }
        acc[resource_name].libraries.push({ ...lib })
        resources_id[resource_id] = resource
      } else {
        console.error(`Resource not found: ${resource_name}`)
      }
    } else {
      // find matched schema 
      let matched_schemas = schemas.filter(
          (schema) => objectMatch(schema.match, lib)
      )
      if (matched_schemas.length === 0){
        matched_schemas = default_schemas.filter(
          (schema) => objectMatch(schema.match, lib)
        )
      }

      if (matched_schemas.length < 1) {
        console.error('Could not match ui-schema for', lib)
        return null
      }
      let name_prop = Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].name)

      if (name_prop.length > 0){
        resource_name = makeTemplate(matched_schemas[0].properties[name_prop[0]].text, lib)
      } else {
        console.warn('source of lib name is not defined, using either dataset or ids')
        resource_name = lib.dataset || lib.id
      }
      let icon_prop = Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].icon)

      if (icon_prop.length > 0){
        icon_src = makeTemplate(matched_schemas[0].properties[icon_prop[0]].src, lib)
        icon_src = icon_src === 'undefined' ? `${process.env.PREFIX}/static/images/default-black.png`: icon_src
      } else {
        console.warn('source of lib icon is not defined, using default')
        icon_src = 'static/images/default-black.png'
      }
      const { Icon, ...rest } = lib.meta
      acc[resource_name] = {
        id: lib.id,
        meta: {
          ...lib.meta,
          Resource_Name: resource_name,
          icon: icon_src || `${process.env.PREFIX}${iconOf[resource_name]}`,
        },
        is_library: true,
        libraries: [lib],
      }
    }
    return acc
  }, {})
  const library_dict = libraries.reduce((L, l) => ({ ...L, [l.id]: l }), {})

  const library_resource = Object.keys(resources).reduce((groups, resource) => {
    for (const library of resources[resource].libraries) {
      groups[library.id] = resource
    }
    return groups
  }, {})
  return {
    libraries: library_dict,
    resources: resources,
    library_resource,
    resources_id,
  }
}

export async function get_signature_counts_per_resources() {
  // const response = await fetch("/resources/all.json").then((res)=>res.json())
  const schemas = await get_schemas("/dcic/signature-commons-schema/v5/meta/schema/ui-schema.json")

  const { libraries, resources, resources_id, library_resource } = await get_library_resources()

  // const count_promises = Object.keys(library_resource).map(async (lib) => {
  //   // request details from GitHub’s API with Axios
  const count_promises = Object.keys(libraries).map(async (lib_key) => {
    const lib = libraries[lib_key]
    // request details from GitHub’s API with Axios
    const { response: stats } = await fetch_meta({
      endpoint: `/libraries/${lib_key}/signatures/count`,
    })
    // Match schema
    let matched_schemas = schemas.filter(
        (schema) => objectMatch(schema.match, lib)
    )
    if (matched_schemas.length === 0){
      matched_schemas = default_schemas.filter(
        (schema) => objectMatch(schema.match, lib)
      )
    }
    if (matched_schemas.length < 1) {
      console.error('Could not match ui-schema for', lib)
      return null
    }
    let name_prop = Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].name)
    let library_name
    if (name_prop.length > 0){
      library_name = makeTemplate(matched_schemas[0].properties[name_prop[0]].text, lib)
    } else {
      console.warn('source of resource name is not defined, using either Library_name or ids')
      library_name = resource.meta['Library_name'] || lib.id
    }

    return {
      id: lib.id,
      name: library_name,
      count: stats.count,
    }
  })
  const counts = await Promise.all(count_promises)
  const count_dict = counts.reduce((acc, item) => {
    acc[item.id] = item.count
    return acc
  }, {})

  const total_count = counts.reduce((acc, item) => {
    acc = acc + item.count
    return acc
  }, 0)

  const resources_with_counts = Object.values(resources).map((resource) => {
    const total_sigs = resource.libraries.reduce((acc, lib) => {
      acc = acc + count_dict[lib.id]
      return acc
    }, 0)
    resource.meta.Signature_Count = total_sigs
    return (resource)
  }).reduce((acc, resource) => {
    let resource_name
    let matched_schemas = schemas.filter(
        (schema) => objectMatch(schema.match, resource)
    )
    if (matched_schemas.length === 0){
      matched_schemas = default_schemas.filter(
        (schema) => objectMatch(schema.match, resource)
      )
    }
    if (matched_schemas.length < 1) {
      console.error('Could not match ui-schema for', resource)
      return null
    }
    let name_prop = Object.keys(matched_schemas[0].properties).filter(prop=> matched_schemas[0].properties[prop].name)
    if (name_prop.length > 0){
      resource_name = makeTemplate(matched_schemas[0].properties[name_prop[0]].text, resource)
    } else {
      console.warn('source of resource name is not defined, using either Resource_Name or ids')
      resource_name = resource.meta['Resource_Name'] || resource_id
    }
    acc[resource_name] = resource
    return acc
  }, {})
  counts.reduce
  const resource_signatures = counts.reduce((groups, lib) => {
    const resource_name = library_resource[lib.id]
    if (groups[resource_name] === undefined) {
      groups[resource_name] = lib.count
    } else {
      groups[resource_name] = groups[resource_name] + lib.count
    }
    if (lib.count !== undefined) {

    }
    return groups
  }, {})

  // let for_sorting = Object.keys(resource_signatures).map(resource=>({name: resource,
  //                                                                    counts: resource_signatures[resource]}))

  // for_sorting.sort(function(a, b) {
  //     return b.counts - a.counts;
  // });
  return {
    resource_signatures: total_count === 0 ? undefined : resource_signatures, // for_sorting.slice(0,11)
    libraries,
    resources: resources_with_counts,
    library_resource,
    resources_id,
  }
}
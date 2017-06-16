// TODO: This could probably be improved, but I'm not a JS expert.


const file_resubmit = {

    cache_key_input_suffix: "_cache_key",

    media_file_basename: "content",

    get_input_cache_key: function (field_name) {
        var l = document.getElementsByName(field_name + this.cache_key_input_suffix);
        if (l.length) {
            var e = l[0];
            return e.defaultValue;
        }
        return null;
    },

    cached_media_file_path: function (cache_key) {
        return cache_key + "/" + this.media_file_basename;
    }
}

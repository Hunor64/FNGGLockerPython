using ICSharpCode.SharpZipLib.Zip.Compression;
using ICSharpCode.SharpZipLib.Zip.Compression.Streams;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Net.Http.Headers;
using System.Text;


class User
{
    public static string AccountId = "";
    public static string UserName = "";
    public static string AccessToken = "";
}

class Program
{
    private static readonly string SWITCH_TOKEN = "OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3";
    private static readonly List<string> ACCEPTED_COSMETIC_TYPES = new List<string>
    {
        "AthenaCharacter",
        "AthenaDance",
        "AthenaPickaxe",
        "AthenaBackpack",
        "AthenaGlider",
        "AthenaItemWrap",
        "AthenaLoadingScreen",
        "AthenaMusicPack",
        "AthenaSkyDiveContrail",
        "BannerToken",
        "HomebaseBannerIcon",
        "SparksSong",
        "SparksGuitar",
        "SparksBass",
        "SparksDrums",
        "SparksKeyboard",
        "SparksMicrophone",
        "SparksAura",
        "VehicleCosmetics_Body",
        "VehicleCosmetics_Skin",
        "VehicleCosmetics_Wheel",
        "VehicleCosmetics_DriftTrail",
        "VehicleCosmetics_Booster",
        "JunoBuildingProp",
        "JunoBuildingSet",
        "CosmeticShoes"
    };

    static async Task Main(string[] args)
    {
        await MainAsync();
    }

    private static async Task MainAsync()
    {
        using (var httpClient = new HttpClient())
        {
            string accessToken = await GetAccessToken(httpClient);
            var (deviceUrl, deviceCode) = await CreateDeviceCode(httpClient, accessToken);
            Console.WriteLine("--> Please log in to your account by opening this link: " + deviceUrl);
            var authData = await WaitForDeviceCodeComplete(httpClient, deviceCode);

            User.AccountId = authData["account_id"].ToString();
            User.UserName = authData["displayName"].ToString();
            User.AccessToken = authData["access_token"].ToString();

            Console.WriteLine($"\n--> Username: {User.UserName}");

            var jsonData = QueryProfile(User.AccountId, "athena", User.AccessToken);
            var jsonDataCc = QueryProfile(User.AccountId, "common_core", User.AccessToken);

            var packsData = await GetPacksData();
            var builtIns = await GetBuiltIns();

            Console.WriteLine("\n--> Processing data");
            var profileItems = ((JObject)jsonData["profileChanges"][0]["profile"]["items"]).ToObject<Dictionary<string, JObject>>().Values.ToList();
            var profileItemsCc = ((JObject)jsonDataCc["profileChanges"][0]["profile"]["items"]).ToObject<Dictionary<string, JObject>>().Values.ToList();

            var filteredItems = profileItems.Where(x => ACCEPTED_COSMETIC_TYPES.Contains(x["templateId"].ToString().Split(':')[0])).ToList();
            var filteredItemsCc = profileItemsCc.Where(x => ACCEPTED_COSMETIC_TYPES.Contains(x["templateId"].ToString().Split(':')[0])).ToList();

// Get the list of cosmetic names (IDs) from the user's owned items
var cosmeticsNames = filteredItems.Select(i => i["templateId"].ToString().Split(':')[1].ToLower()).ToList();

// Get the list of banners from common_core profile items
var banners = filteredItemsCc.Select(i => i["templateId"].ToString().Split(':')[1].ToLower()).ToList();

// Find the built-in emote IDs associated with the skins you own
var builtInEmoteIds = builtIns
    .Where(b => cosmeticsNames.Contains(b.Key.ToLower()))
    .Select(b => b.Value.ToLower())
    .ToList();

            // Add banners and built-in emotes to the list of cosmetic names
            cosmeticsNames.AddRange(banners);
            cosmeticsNames.AddRange(builtInEmoteIds);
            Console.WriteLine("\n--> Requesting data from https://fortnite.gg");
            var fnggDataRequest = await GetJsonAsync("https://fortnite.gg/api/items.json");
            var fnggBundleData = await GetJsonAsync("https://fortnite.gg/api/bundles.json");

            Console.WriteLine("\n--> Processing data");
            // Adjust the ToDictionary call to handle duplicate keys
            var fnggData = ((JObject)JObject.FromObject(fnggDataRequest))
    .ToObject<Dictionary<string, int>>()
    .GroupBy(i => i.Key.ToLower())
    .ToDictionary(g => g.Key, g => g.First().Value);
            var athenaCreationDate = ((JObject)jsonData["profileChanges"][0]["profile"])["created"]?.ToString();

            var ownedBundles = fnggBundleData.Keys
                .Select(i => CheckBundle(i, fnggBundleData[i], cosmeticsNames, fnggData))
                .Where(x => x != null)
                .ToList();
            // **Define 'packs' here**
            var packs = packsData.Keys
                .Where(i => cosmeticsNames.Contains(i))
                .Select(i => packsData[i])
                .Distinct()
                .ToList();
            // Parse the string IDs in 'packs' to integers
            var ints = fnggData
                .Where(i => cosmeticsNames.Contains(i.Key))
                .Select(i => i.Value)
                .Concat(packs.Select(p => int.Parse(p)))
                .Concat(ownedBundles.Where(x => x.HasValue).Select(x => x.Value))
                .Distinct()
                .OrderBy(i => i)
                .ToList();


            var diff = ints.Select((e, index) => index > 0 ? (e - ints[index - 1]).ToString() : e.ToString()).ToList();

            var compressed = CompressData($"{athenaCreationDate},{string.Join(",", diff)}");

            Console.WriteLine("\n--> Encoding data");

            // Use Base64UrlEncode method
            var encoded = Base64UrlEncode(compressed).TrimEnd('=');

            Console.WriteLine($"\n\n--> Your locker: https://fortnite.gg/my-locker?items={encoded}");

            Console.ReadLine();

            await File.WriteAllTextAsync("locker.txt", $"https://fortnite.gg/my-locker?items={encoded}");

        }
    }

    private static async Task<string> GetAccessToken(HttpClient httpClient)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token");
        request.Headers.Authorization = new AuthenticationHeaderValue("basic", SWITCH_TOKEN);
        request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            { "grant_type", "client_credentials" }
        });

        var response = await httpClient.SendAsync(request);
        var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
        return data["access_token"].ToString();
    }

    private static async Task<(string, string)> CreateDeviceCode(HttpClient httpClient, string accessToken)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization");
        request.Headers.Authorization = new AuthenticationHeaderValue("bearer", accessToken);
        request.Content = new StringContent(string.Empty, Encoding.UTF8, "application/x-www-form-urlencoded");

        var response = await httpClient.SendAsync(request);
        var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
        return (data["verification_uri_complete"].ToString(), data["device_code"].ToString());
    }

    private static async Task<Dictionary<string, object>> WaitForDeviceCodeComplete(HttpClient httpClient, string code)
    {
        while (true)
        {
            var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token");
            request.Headers.Authorization = new AuthenticationHeaderValue("basic", SWITCH_TOKEN);
            request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                { "grant_type", "device_code" },
                { "device_code", code }
            });

            var response = await httpClient.SendAsync(request);
            if (response.StatusCode == System.Net.HttpStatusCode.OK)
            {
                var authData = JsonConvert.DeserializeObject<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
                return authData;
            }

            await Task.Delay(3000);
        }
    }

    private static JObject QueryProfile(string accountId, string profileId, string bearer)
    {
        var reqUrl = $"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountId}/client/QueryProfile?profileId={profileId}";

        using (var client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("bearer", bearer);
            var response = client.PostAsync(reqUrl, new StringContent(JsonConvert.SerializeObject(new { }), Encoding.UTF8, "application/json")).Result;
            return JObject.Parse(response.Content.ReadAsStringAsync().Result);
        }
    }

    // Update the GetPacksData method
    private static async Task<Dictionary<string, string>> GetPacksData()
    {
        using (var httpClient = new HttpClient())
        {
            var response = await httpClient.GetStringAsync("https://api.fecooo.hu/fngg/offers");
            return JsonConvert.DeserializeObject<Dictionary<string, string>>(response);
        }
    }

    // Update the GetBuiltIns method
    private static async Task<Dictionary<string, string>> GetBuiltIns()
    {
        using (var httpClient = new HttpClient())
        {
            var response = await httpClient.GetStringAsync("https://api.fecooo.hu/fngg/builtins");
            return JsonConvert.DeserializeObject<Dictionary<string, string>>(response);
        }
    }

    private static async Task<Dictionary<string, object>> GetJsonAsync(string url)
    {
        using (var httpClient = new HttpClient())
        {
            var response = await httpClient.GetStringAsync(url);
            return JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
        }
    }

    private static int? CheckBundle(string bundleId, object data, List<string> profileItems, Dictionary<string, int> fnggItems)
    {
        var items = ((JArray)((JObject)data)["items"]).ToObject<List<object>>();
        var countOfShould = items.Count;
        var countOfActual = items.Count(i => profileItems.Contains(i.ToString().ToLower()));

        if (countOfShould == countOfActual)
        {
            return fnggItems[bundleId.ToLower()];
        }
        else
        {
            return null;
        }
    }

    // Modify the CompressData method
    private static byte[] CompressData(string data)
    {
        var inputBytes = Encoding.UTF8.GetBytes(data);
        using (var outputStream = new MemoryStream())
        {
            var deflater = new Deflater(Deflater.DEFAULT_COMPRESSION, true); // 'true' for no ZLIB headers
            using (var compressor = new DeflaterOutputStream(outputStream, deflater))
            {
                compressor.IsStreamOwner = false;
                compressor.Write(inputBytes, 0, inputBytes.Length);
                compressor.Flush();
                compressor.Finish();
            }
            return outputStream.ToArray();
        }
    }
    public static string Base64UrlEncode(byte[] input)
    {
        string base64 = Convert.ToBase64String(input).TrimEnd('=');
        return base64.Replace('+', '-').Replace('/', '_');
    }
}


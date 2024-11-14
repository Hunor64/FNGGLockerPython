using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;
using System.Diagnostics;

namespace FNGG_Forms
{
public class User
    {
        public static string AccountId = "";
        public static string UserName = "";
        public static string AccessToken = "";
    }

    public class Program
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
        "JunoBuildingSet"
    };

        public static async Task Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            var form = new MainForm();
            Application.Run(form);
        }

        public static async Task<string> GetAccessToken(HttpClient httpClient)
        {
            var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token");
            request.Headers.Add("Authorization", $"basic {SWITCH_TOKEN}");
            request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            { "grant_type", "client_credentials" }
        });

            var response = await httpClient.SendAsync(request);
            var data = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
            return data["access_token"];
        }

        public static async Task<(string, string)> CreateDeviceCode(HttpClient httpClient, string accessToken)
        {
            var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization");
            request.Headers.Add("Authorization", $"bearer {accessToken}");
            request.Content = new StringContent(string.Empty, Encoding.UTF8, "application/x-www-form-urlencoded");

            var response = await httpClient.SendAsync(request);
            var data = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
            return (data["verification_uri_complete"], data["device_code"]);
        }

        public static async Task<Dictionary<string, string>> WaitForDeviceCodeComplete(HttpClient httpClient, string code)
        {
            while (true)
            {
                var request = new HttpRequestMessage(HttpMethod.Post, "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token");
                request.Headers.Add("Authorization", $"basic {SWITCH_TOKEN}");
                request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                { "grant_type", "device_code" },
                { "device_code", code }
            });

                var response = await httpClient.SendAsync(request);
                if (response.StatusCode == System.Net.HttpStatusCode.OK)
                {
                    return JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
                }

                await Task.Delay(3000);
            }
        }

        public static void OpenLink(string url)
        {
            Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
        }

        public static string GetJsonPath(string filename)
        {
            return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, filename);
        }

        public static async Task<Dictionary<string, object>> QueryProfile(string accountId, string profileId, string bearer)
        {
            var reqUrl = $"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountId}/client/QueryProfile?profileId={profileId}";
            using (var httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Add("Authorization", $"bearer {bearer}");
                httpClient.DefaultRequestHeaders.Add("Content-Type", "application/json");
                var response = await httpClient.PostAsync(reqUrl, new StringContent(JsonConvert.SerializeObject(new { }), Encoding.UTF8, "application/json"));
                return JsonConvert.DeserializeObject<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
            }
        }

        public static int? CheckBundle(string bundleId, Dictionary<string, object> data, List<string> profileItems, Dictionary<string, int> fnggItems)
        {
            int countOfShould = ((List<object>)data["items"]).Count;
            int countOfActual = 0;

            foreach (var item in (List<object>)data["items"])
            {
                if (profileItems.Contains(item.ToString().ToLower()))
                {
                    countOfActual++;
                }
            }

            if (countOfShould == countOfActual)
            {
                return fnggItems[bundleId.ToLower()];
            }
            else
            {
                return null;
            }
        }
    }

    public class MainForm : Form
    {
        private Button startAuthButton;
        private Label statusLabel;

        public MainForm()
        {
            Text = "FNGG Locker";
            Size = new System.Drawing.Size(300, 300);
            startAuthButton = new Button { Text = "Start Authentication", Dock = DockStyle.Bottom };
            startAuthButton.Click += StartAuthButton_Click;
            Controls.Add(startAuthButton);
            statusLabel = new Label { Dock = DockStyle.Top, TextAlign = System.Drawing.ContentAlignment.MiddleCenter };
            Controls.Add(statusLabel);
        }

        private async void StartAuthButton_Click(object sender, EventArgs e)
        {
            startAuthButton.Enabled = false;
            statusLabel.Text = "Authenticating...";
            using (var httpClient = new HttpClient())
            {
                var accessToken = await Program.GetAccessToken(httpClient);
                var (deviceUrl, deviceCode) = await Program.CreateDeviceCode(httpClient, accessToken);
                statusLabel.Text = "Please log in to your account by clicking this link.";
                var linkLabel = new LinkLabel { Text = "Click here to log in", Dock = DockStyle.Top };
                linkLabel.LinkClicked += (s, args) => Program.OpenLink(deviceUrl);
                Controls.Add(linkLabel);
                var authData = await Program.WaitForDeviceCodeComplete(httpClient, deviceCode);
                User.AccountId = authData["account_id"];
                User.UserName = authData["displayName"];
                User.AccessToken = authData["access_token"];
                statusLabel.Text = $"Username: {User.UserName}";
            }
            startAuthButton.Enabled = true;
        }
    }


}

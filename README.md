## Env files

This project reads credentials from a `.env.local` file (not commited in Git), which should have:

* `OAUTH_CLIENT_ID`
* `OAUTH_CLIENT_SECRET`
* `GOOGLE_ADS_DEV_TOKEN`

Check "Prerequisites" below on how to obtain those

## Usage

Invoke the python module from the cli. For example:
With keywords:

```bash
python -m seo_keyword_planner fetch --keywords "car"
```

With an url:

```bash
python -m seo_keyword_planner fetch --url "www.example.com"
```

The first time you log in, a browser window will open where you can log into your Google account.
After that, if there are multiple Google Ads accounts associated with the same Google account,
you'll be prompted to select which one you want to use. You can check the id of any account
by going to https://ads.google.com/aw/campaigns and looking in the top right corner for a
number that looks like 123-456-7890.
Also, the program might output a link you must click to enable the API.

## Prerequisites

Unfortunately, there is a bit of configuration necessary to get this
working. [This article](https://developers.google.com/google-ads/api/docs/oauth/overview) includes a video explaining
why each one is necessary.

### Google Ads Account

Use an existing account or create a new one by going
to [this url](https://ads.google.com/um/StartNow?sourceid=awo&subid=ww-ww-et-awhc-6366720) and
following [these instructions](https://support.google.com/google-ads/answer/6366720?hl=en)

### Developer Token

A developer token is a 22 alphanumeric code necessary to query the API.
To obtain it, you must first have a manager account. You can create one with a couple of clicks
by going to [this url](https://ads.google.com/home/tools/manager-accounts/) and following
[these instructions](https://support.google.com/google-ads/answer/7459399?hl=en)

Then, on the manager account,
follow [these instructions](https://developers.google.com/google-ads/api/docs/get-started/dev-token#find-token)
You can also go directly to [this link](https://ads.google.com/aw/apicenter) for the API Center. You
will have to complete a simple form to apply for the developer token, but access should be granted immediately.

Save this in `GOOGLE_ADS_DEV_TOKEN`

### Test Account (optional)

If you already have a **Basic token**, achieved by
filling [this more complex form](https://support.google.com/adspolicy/contact/new_token_application),
after the form in the previous step, this step is not necessary.

Otherwise, you have a **Test token**, which has very limited privileges, but it will work fine for just querying the
Keywords API.
The only caveat of Test tokens is that they can only access **Test accounts**.
You can create one ([instructions here](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts))
in a couple of clicks by going to [this url](https://ads.google.com/nav/selectaccount?sf=mt), clicking "New Google Ads
account" and filling some basic info.

### OAuth credentials

Finally, to allow users to sign in with Google account, you must create OAuth credentials. These
are not super-sensitive because, by themselves, don't grant any access, only allow users to
use their Google credentials to authenticate in that Google Ads project.

Just go to [this link](https://console.cloud.google.com/apis/credentials/oauthclient) with the
same account you created the project and follow very basic instructions (you can select "Desktop App").
You will end up in a page with "Client ID" and "Client Secret Key", please add them both to
`OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`

## Multiple users

If you have multiple users in that same Google Ads project, they can share OAuth credentials and
the developer token. The only extra configuration is that if you have a Test token (refer to "Test Account" above),
all users that want to use the API need a Test Account linked to the project.
